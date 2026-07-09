# -*- coding: utf-8 -*-
"""Aggregated tax summaries for GSTR-3B style boards."""

from odoo import fields, models


class RnGstSummary(models.Model):
    """Stores section totals for a return (output, input, RCM, etc.)."""

    _name = 'rn.gst.summary'
    _description = 'GST Summary'
    _order = 'sequence, id'

    return_id = fields.Many2one('rn.gst.return', required=True, ondelete='cascade', index=True)
    name = fields.Char(required=True)
    sequence = fields.Integer(default=10)
    summary_type = fields.Selection(
        selection=[
            ('output', 'Output GST'),
            ('input', 'Input GST'),
            ('rcm', 'Reverse Charge'),
            ('itc', 'ITC Available'),
            ('net', 'Net Payable'),
            ('other', 'Other'),
        ],
        default='other',
        required=True,
    )
    taxable_amount = fields.Monetary(currency_field='currency_id')
    cgst_amount = fields.Monetary(currency_field='currency_id')
    sgst_amount = fields.Monetary(currency_field='currency_id')
    igst_amount = fields.Monetary(currency_field='currency_id')
    cess_amount = fields.Monetary(currency_field='currency_id')
    total_tax = fields.Monetary(currency_field='currency_id')
    currency_id = fields.Many2one(related='return_id.currency_id', store=True)
    company_id = fields.Many2one(related='return_id.company_id', store=True)
