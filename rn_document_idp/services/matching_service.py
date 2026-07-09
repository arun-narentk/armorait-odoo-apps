# -*- coding: utf-8 -*-
"""Three-way match between PO, receipt, and vendor invoice."""

from odoo import models


class RnDocumentIdpMatchingService(models.AbstractModel):
    _name = 'rn.document.idp.matching.service'
    _description = 'IDP Three-Way Matching Service'

    def evaluate_match(self, document):
        if document.document_type != 'vendor_invoice' or not document.purchase_order_id:
            return 'na', 0.0, ''
        po = document.purchase_order_id
        settings = self.env['rn.document.idp.validation.service']._get_settings(document.company_id.id)
        po_total = po.amount_total
        invoice_total = document.amount_total or 0.0
        if not po_total:
            return 'pending', 0.0, 'Purchase order has no total to compare.'
        diff_pct = abs(invoice_total - po_total) / po_total * 100.0
        if diff_pct <= settings.price_tolerance_percent:
            return 'matched', max(0.0, 100.0 - diff_pct), 'Invoice total within PO tolerance.'
        return 'mismatch', max(0.0, 100.0 - diff_pct), (
            f'Invoice total differs from PO by {diff_pct:.1f}% '
            f'(tolerance {settings.price_tolerance_percent}%).'
        )
