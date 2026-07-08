# -*- coding: utf-8 -*-
"""GST reconciliation batches and mismatch lines."""

from odoo import fields, models


class RnGstReconciliation(models.Model):
    """Header for a purchase/sales vs GST mismatch review."""

    _name = 'rn.gst.reconciliation'
    _description = 'GST Reconciliation'
    _inherit = ['mail.thread']
    _order = 'id desc'

    name = fields.Char(required=True, default='GST Reconciliation')
    period_id = fields.Many2one('rn.gst.period', required=True)
    reconciliation_type = fields.Selection(
        selection=[
            ('purchase_itc', 'Purchase vs Input Tax'),
            ('sales_output', 'Sales vs Output Tax'),
            ('duplicate', 'Duplicate Detection'),
            ('missing_gstin', 'Missing GSTIN'),
            ('missing_hsn', 'Missing HSN'),
            ('tax_diff', 'Tax Difference'),
            ('invoice_diff', 'Invoice Difference'),
            ('vendor_diff', 'Vendor Difference'),
        ],
        required=True,
    )
    state = fields.Selection(
        selection=[
            ('draft', 'Draft'),
            ('done', 'Done'),
            ('cancelled', 'Cancelled'),
        ],
        default='draft',
        tracking=True,
    )
    mismatch_count = fields.Integer()
    line_ids = fields.One2many('rn.gst.reconciliation.line', 'reconciliation_id', string='Lines')
    company_id = fields.Many2one(
        'res.company',
        required=True,
        default=lambda self: self.env.company,
    )
    notes = fields.Text()


class RnGstReconciliationLine(models.Model):
    """Single mismatch row for a reconciliation batch."""

    _name = 'rn.gst.reconciliation.line'
    _description = 'GST Reconciliation Line'
    _order = 'id'

    reconciliation_id = fields.Many2one(
        'rn.gst.reconciliation',
        required=True,
        ondelete='cascade',
        index=True,
    )
    name = fields.Char(required=True)
    move_id = fields.Many2one('account.move')
    partner_id = fields.Many2one('res.partner')
    expected_amount = fields.Float(digits=(16, 2))
    actual_amount = fields.Float(digits=(16, 2))
    difference = fields.Float(digits=(16, 2))
    recommendation = fields.Text()
    company_id = fields.Many2one(related='reconciliation_id.company_id', store=True)
