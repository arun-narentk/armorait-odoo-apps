# -*- coding: utf-8 -*-
"""Fuzzy vendor matching."""

import logging
import re

from odoo import models

_logger = logging.getLogger(__name__)


def _normalize(text):
    if not text:
        return ''
    text = text.lower()
    text = re.sub(r'[^a-z0-9]', '', text)
    for token in ('pvtltd', 'privatelimited', 'limited', 'ltd'):
        text = text.replace(token, '')
    return text


class RnAiInvoiceVendorMatchService(models.AbstractModel):
    """Match OCR vendor name and GSTIN to res.partner."""

    _name = 'rn.ai.invoice.vendor.match.service'
    _description = 'Invoice Vendor Match Service'

    def match_vendor(self, ocr_name, gstin=None, company_id=None):
        company_id = company_id or self.env.company.id
        Partner = self.env['res.partner']

        if gstin:
            partner = Partner.search([
                ('vat', '=ilike', gstin),
                '|', ('company_id', '=', company_id), ('company_id', '=', False),
            ], limit=1)
            if partner:
                self._record_mapping(ocr_name, partner, company_id)
                return partner, 99.0

        if not ocr_name:
            return Partner, 0.0

        mapping = self.env['rn.ai.invoice.vendor.mapping'].search([
            ('ocr_text', '=ilike', ocr_name.strip()),
            ('company_id', '=', company_id),
        ], limit=1)
        if mapping:
            return mapping.partner_id, 98.0

        norm_ocr = _normalize(ocr_name)
        best_partner = Partner
        best_score = 0.0
        candidates = Partner.search([
            ('supplier_rank', '>', 0),
            '|', ('company_id', '=', company_id), ('company_id', '=', False),
        ], limit=200)
        for partner in candidates:
            norm_name = _normalize(partner.name)
            if not norm_name:
                continue
            if norm_ocr == norm_name:
                score = 99.0
            elif norm_ocr in norm_name or norm_name in norm_ocr:
                score = 85.0
            else:
                continue
            if score > best_score:
                best_score = score
                best_partner = partner

        if best_score >= 80:
            self._record_mapping(ocr_name, best_partner, company_id)
        return best_partner, best_score

    def _record_mapping(self, ocr_text, partner, company_id):
        if not ocr_text or not partner:
            return
        Mapping = self.env['rn.ai.invoice.vendor.mapping']
        existing = Mapping.search([
            ('ocr_text', '=ilike', ocr_text.strip()),
            ('company_id', '=', company_id),
        ], limit=1)
        if existing:
            existing.hit_count += 1
        else:
            Mapping.create({
                'ocr_text': ocr_text.strip(),
                'partner_id': partner.id,
                'company_id': company_id,
            })
