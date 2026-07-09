# -*- coding: utf-8 -*-
"""Confirm vendor bill creation from scan."""

from odoo import fields, models


class RnAiInvoiceCreateBillWizard(models.TransientModel):
    _name = 'rn.ai.invoice.create.bill.wizard'
    _description = 'Create Vendor Bill from OCR Scan'

    scan_id = fields.Many2one('rn.ai.invoice.scan', required=True)
    partner_id = fields.Many2one('res.partner', related='scan_id.partner_id', readonly=False)
    invoice_number = fields.Char(related='scan_id.invoice_number', readonly=False)
    amount_total = fields.Monetary(related='scan_id.amount_total', readonly=False)
    currency_id = fields.Many2one(related='scan_id.currency_id')
    is_duplicate = fields.Boolean(related='scan_id.is_duplicate')
    confirm_duplicate = fields.Boolean(
        string='Create anyway (duplicate warning)',
        help='Check to create bill even if duplicate was detected.',
    )

    def action_create_bill(self):
        self.ensure_one()
        if self.scan_id.is_duplicate and not self.confirm_duplicate:
            from odoo.exceptions import UserError
            raise UserError('Duplicate invoice detected. Enable confirm to proceed.')
        return self.scan_id.action_create_vendor_bill()
