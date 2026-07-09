# -*- coding: utf-8 -*-
"""Validation issue records for GST returns and invoices."""

from odoo import fields, models


class RnGstValidation(models.Model):
    """One validation finding (error/warning) for a return or move."""

    _name = 'rn.gst.validation'
    _description = 'GST Validation Issue'
    _order = 'severity desc, id desc'

    name = fields.Char(required=True)
    return_id = fields.Many2one('rn.gst.return', ondelete='cascade', index=True)
    move_id = fields.Many2one('account.move', string='Invoice', index=True)
    partner_id = fields.Many2one('res.partner')
    issue_type = fields.Selection(
        selection=[
            ('gstin', 'GSTIN'),
            ('hsn', 'HSN'),
            ('sac', 'SAC'),
            ('invoice_number', 'Invoice Number'),
            ('invoice_date', 'Invoice Date'),
            ('invoice_sequence', 'Invoice Sequence'),
            ('tax_amount', 'Tax Amount'),
            ('cgst', 'CGST'),
            ('sgst', 'SGST'),
            ('igst', 'IGST'),
            ('cess', 'CESS'),
            ('reverse_charge', 'Reverse Charge'),
            ('pos', 'Place of Supply'),
            ('state_code', 'State Code'),
            ('duplicate', 'Duplicate Invoice'),
            ('missing_tax', 'Missing Tax'),
            ('missing_gstin', 'Missing Partner GSTIN'),
            ('missing_hsn', 'Missing HSN'),
            ('missing_sac', 'Missing SAC'),
            ('other', 'Other'),
        ],
        required=True,
        index=True,
    )
    severity = fields.Selection(
        selection=[
            ('info', 'Info'),
            ('warning', 'Warning'),
            ('error', 'Error'),
            ('critical', 'Critical'),
        ],
        default='error',
        required=True,
        index=True,
    )
    message = fields.Text(required=True)
    state = fields.Selection(
        selection=[
            ('open', 'Open'),
            ('resolved', 'Resolved'),
            ('ignored', 'Ignored'),
        ],
        default='open',
    )
    company_id = fields.Many2one(
        'res.company',
        required=True,
        default=lambda self: self.env.company,
    )
