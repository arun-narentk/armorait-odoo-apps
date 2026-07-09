# -*- coding: utf-8 -*-
"""Main IDP processing pipeline."""

from __future__ import annotations

import logging
import time

from odoo import fields, models

_logger = logging.getLogger(__name__)


class RnDocumentIdpPipelineService(models.AbstractModel):
    _name = 'rn.document.idp.pipeline.service'
    _description = 'IDP Pipeline Service'

    def process_document(self, document):
        start = time.time()
        settings = self._get_settings(document.company_id.id)
        if settings.credit_balance <= 0:
            document.message_post(body='Document credit balance is zero. Add credits to continue.')
            document.write({'state': 'draft'})
            return False

        raw_text = self.env['rn.document.idp.ocr.service'].extract_text(document.attachment_id)
        doc_type, type_conf = self.env['rn.document.idp.classification.service'].classify(raw_text)
        extracted = self.env['rn.document.idp.extraction.service'].extract(raw_text, doc_type)
        partner, partner_conf = self._match_partner(extracted, document.company_id.id)
        dup_move = self.env['rn.document.idp.duplicate.service'].find_duplicate_bill(
            partner.id if partner else False,
            extracted.get('document_number'),
            company_id=document.company_id.id,
        )
        fraud_score, fraud_notes = self._detect_fraud_signals(document, extracted, partner)

        document.line_ids.unlink()
        line_confs = []
        Line = self.env['rn.document.idp.line']
        for idx, line in enumerate(extracted.get('lines', [])):
            product = self._match_product(line.get('description'), document.company_id.id)
            conf = 80.0 if product else 50.0
            line_confs.append(conf)
            Line.create({
                'document_id': document.id,
                'sequence': (idx + 1) * 10,
                'description': line.get('description'),
                'product_id': product.id if product else False,
                'quantity': line.get('quantity', 1.0),
                'price_unit': line.get('price_unit', 0.0),
                'tax_percent': line.get('tax_percent', 0.0),
                'price_subtotal': line.get('price_subtotal', 0.0),
                'confidence': conf,
            })

        line_confidence = round(sum(line_confs) / len(line_confs), 1) if line_confs else 0.0
        document.write({
            'raw_text': raw_text,
            'document_type': doc_type,
            'document_type_confidence': type_conf,
            'partner_name_extracted': extracted.get('partner_name'),
            'partner_id': partner.id if partner else False,
            'partner_confidence': partner_conf,
            'gstin': extracted.get('gstin'),
            'document_number': extracted.get('document_number'),
            'document_date': extracted.get('document_date'),
            'due_date': extracted.get('due_date'),
            'amount_untaxed': extracted.get('amount_untaxed'),
            'amount_tax': extracted.get('amount_tax'),
            'amount_total': extracted.get('amount_total'),
            'amount_confidence': 95.0 if extracted.get('amount_total') else 0.0,
            'line_confidence': line_confidence,
            'is_duplicate': bool(dup_move),
            'duplicate_move_id': dup_move.id if dup_move else False,
            'fraud_score': fraud_score,
            'fraud_notes': fraud_notes,
            'state': 'classified',
            'processing_seconds': round(time.time() - start, 2),
        })

        validation_state = self.env['rn.document.idp.validation.service'].run_validations(
            document, extracted, partner,
        )
        match_state, match_score, match_note = self.env['rn.document.idp.matching.service'].evaluate_match(
            document,
        )
        state = 'duplicate' if dup_move else 'review'
        if fraud_score >= settings.fraud_alert_threshold:
            state = 'fraud_flag'
        elif validation_state == 'passed' and document.overall_confidence >= settings.auto_post_confidence:
            state = 'approved'

        document.write({
            'validation_state': validation_state,
            'match_state': match_state,
            'match_score': match_score,
            'state': state,
        })
        if match_note:
            document.message_post(body=match_note)
        settings.credit_balance -= 1
        document.message_post(body='IDP pipeline completed. Review validation results.')
        return True

    def _match_partner(self, extracted, company_id):
        Partner = self.env['res.partner']
        gstin = extracted.get('gstin')
        name = extracted.get('partner_name')
        if gstin:
            partner = Partner.search([
                ('vat', '=ilike', gstin),
                '|', ('company_id', '=', company_id), ('company_id', '=', False),
            ], limit=1)
            if partner:
                return partner, 98.0
        if name:
            partner = Partner.search([
                ('name', 'ilike', name),
                '|', ('company_id', '=', company_id), ('company_id', '=', False),
            ], limit=1)
            if partner:
                return partner, 85.0
        return self.env['res.partner'], 0.0

    def _match_product(self, description, company_id):
        if not description:
            return self.env['product.product']
        return self.env['product.product'].search([
            ('name', 'ilike', description[:40]),
            '|', ('company_id', '=', company_id), ('company_id', '=', False),
        ], limit=1)

    def _detect_fraud_signals(self, document, extracted, partner):
        score = 0.0
        notes = []
        total = extracted.get('amount_total') or 0.0
        if total > 1000000:
            score += 25.0
            notes.append('High value document detected.')
        if not partner and total > 50000:
            score += 35.0
            notes.append('New or unknown supplier with significant amount.')
        tax = extracted.get('amount_tax') or 0.0
        untaxed = extracted.get('amount_untaxed') or 0.0
        if untaxed and tax / untaxed > 0.28:
            score += 20.0
            notes.append('Unusual tax percentage detected.')
        return min(score, 100.0), '\n'.join(notes)

    def _get_settings(self, company_id):
        Settings = self.env['rn.document.idp.settings']
        settings = Settings.search([('company_id', '=', company_id)], limit=1)
        if not settings:
            settings = Settings.create({'name': 'IDP Settings', 'company_id': company_id})
        return settings
