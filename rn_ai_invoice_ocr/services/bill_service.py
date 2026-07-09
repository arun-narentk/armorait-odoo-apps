# -*- coding: utf-8 -*-
"""Create account.move vendor bill from scan."""

import logging

from odoo import fields, models
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class RnAiInvoiceBillService(models.AbstractModel):
    """Build draft vendor bill from reviewed OCR scan."""

    _name = 'rn.ai.invoice.bill.service'
    _description = 'Invoice Bill Service'

    def create_vendor_bill(self, scan):
        if not scan.partner_id:
            raise UserError('Select or match a vendor before creating the bill.')
        journal = self._get_purchase_journal(scan.company_id.id)
        line_vals = []
        for line in scan.line_ids:
            line_vals.append((0, 0, {
                'name': line.description,
                'product_id': line.product_id.id if line.product_id else False,
                'quantity': line.quantity or 1.0,
                'price_unit': line.price_unit,
                'discount': line.discount,
            }))
        if not line_vals:
            line_vals.append((0, 0, {
                'name': scan.invoice_number or 'Invoice line',
                'quantity': 1.0,
                'price_unit': scan.amount_total or scan.amount_untaxed or 0.0,
            }))
        move = self.env['account.move'].create({
            'move_type': 'in_invoice',
            'partner_id': scan.partner_id.id,
            'invoice_date': scan.invoice_date or fields.Date.context_today(self),
            'invoice_date_due': scan.due_date,
            'ref': scan.invoice_number,
            'journal_id': journal.id,
            'company_id': scan.company_id.id,
            'invoice_line_ids': line_vals,
            'narration': f'Created from AI Invoice OCR scan {scan.reference}',
        })
        scan.message_post(body=f'Vendor bill {move.name} created from OCR scan.')
        return move

    def _get_purchase_journal(self, company_id):
        settings = self.env['rn.ai.invoice.ocr.settings'].search(
            [('company_id', '=', company_id)], limit=1,
        )
        if settings and settings.purchase_journal_id:
            return settings.purchase_journal_id
        journal = self.env['account.journal'].search([
            ('type', '=', 'purchase'),
            ('company_id', '=', company_id),
        ], limit=1)
        if not journal:
            raise UserError('Configure a purchase journal for vendor bills.')
        return journal
