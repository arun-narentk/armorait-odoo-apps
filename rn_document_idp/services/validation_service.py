# -*- coding: utf-8 -*-
"""Business validation before ERP posting."""

from __future__ import annotations

import re

from odoo import models

GSTIN_RE = re.compile(r'^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z][1-9A-Z]Z[0-9A-Z]$')


class RnDocumentIdpValidationService(models.AbstractModel):
    _name = 'rn.document.idp.validation.service'
    _description = 'IDP Validation Service'

    def run_validations(self, document, extracted, partner):
        Validation = self.env['rn.document.idp.validation']
        document.validation_ids.unlink()
        results = []
        settings = self._get_settings(document.company_id.id)

        results.append(self._check_vendor_exists(document, partner))
        if extracted.get('gstin') and settings.enable_gst_india:
            results.append(self._check_gst_format(extracted.get('gstin')))
        if settings.enable_duplicate_check:
            results.append(self._check_duplicate(document, partner, extracted))
        if document.purchase_order_id and settings.enable_three_way_match:
            results.append(self._check_po_exists(document))
        results.append(self._check_currency(document))
        results.append(self._check_tax_totals(extracted))
        results.append(self._check_confidence(document))

        for item in results:
            Validation.create({
                'document_id': document.id,
                'rule_code': item['code'],
                'name': item['name'],
                'state': item['state'],
                'message': item.get('message', ''),
            })

        failed = any(item['state'] == 'failed' for item in results)
        warnings = any(item['state'] == 'warning' for item in results)
        if failed:
            return 'failed'
        if warnings:
            return 'failed'
        return 'passed'

    def _check_vendor_exists(self, document, partner):
        if document.document_type not in ('vendor_invoice', 'expense_receipt'):
            return {'code': 'vendor_exists', 'name': 'Vendor Exists', 'state': 'passed'}
        if partner:
            return {'code': 'vendor_exists', 'name': 'Vendor Exists', 'state': 'passed'}
        return {
            'code': 'vendor_exists',
            'name': 'Vendor Exists',
            'state': 'failed',
            'message': 'No matching vendor found in Odoo.',
        }

    def _check_gst_format(self, gstin):
        valid = bool(GSTIN_RE.match((gstin or '').upper()))
        return {
            'code': 'gst_format',
            'name': 'GSTIN Format',
            'state': 'passed' if valid else 'failed',
            'message': '' if valid else f'Invalid GSTIN format: {gstin}',
        }

    def _check_duplicate(self, document, partner, extracted):
        dup_bill = self.env['rn.document.idp.duplicate.service'].find_duplicate_bill(
            partner.id if partner else False,
            extracted.get('document_number'),
            company_id=document.company_id.id,
        )
        if dup_bill:
            return {
                'code': 'duplicate_invoice',
                'name': 'Duplicate Invoice',
                'state': 'failed',
                'message': f'Existing vendor bill {dup_bill.name} matches this document number.',
            }
        return {'code': 'duplicate_invoice', 'name': 'Duplicate Invoice', 'state': 'passed'}

    def _check_po_exists(self, document):
        if document.purchase_order_id.state in ('purchase', 'done'):
            return {'code': 'po_exists', 'name': 'Purchase Order Exists', 'state': 'passed'}
        return {
            'code': 'po_exists',
            'name': 'Purchase Order Exists',
            'state': 'failed',
            'message': 'Linked purchase order is not confirmed.',
        }

    def _check_currency(self, document):
        if document.currency_id:
            return {'code': 'currency_supported', 'name': 'Currency Supported', 'state': 'passed'}
        return {
            'code': 'currency_supported',
            'name': 'Currency Supported',
            'state': 'failed',
            'message': 'Currency could not be resolved.',
        }

    def _check_tax_totals(self, extracted):
        total = extracted.get('amount_total') or 0.0
        untaxed = extracted.get('amount_untaxed') or 0.0
        tax = extracted.get('amount_tax') or 0.0
        if not total:
            return {
                'code': 'tax_totals',
                'name': 'Tax Totals',
                'state': 'warning',
                'message': 'Total amount not detected.',
            }
        if abs((untaxed + tax) - total) > max(1.0, total * 0.02):
            return {
                'code': 'tax_totals',
                'name': 'Tax Totals',
                'state': 'warning',
                'message': 'Untaxed + tax does not match total within tolerance.',
            }
        return {'code': 'tax_totals', 'name': 'Tax Totals', 'state': 'passed'}

    def _check_confidence(self, document):
        settings = self._get_settings(document.company_id.id)
        if document.overall_confidence >= settings.auto_post_confidence:
            return {'code': 'confidence', 'name': 'Confidence Score', 'state': 'passed'}
        return {
            'code': 'confidence',
            'name': 'Confidence Score',
            'state': 'warning',
            'message': f'Confidence {document.overall_confidence}% is below auto-post threshold.',
        }

    def _get_settings(self, company_id):
        Settings = self.env['rn.document.idp.settings']
        settings = Settings.search([('company_id', '=', company_id)], limit=1)
        if not settings:
            settings = Settings.create({'name': 'IDP Settings', 'company_id': company_id})
        return settings
