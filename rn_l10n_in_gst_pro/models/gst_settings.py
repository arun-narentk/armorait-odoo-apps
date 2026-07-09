# -*- coding: utf-8 -*-
"""Per-company GST Pro settings."""

from odoo import fields, models


class RnGstSettings(models.Model):
    """Company GST compliance configuration used by exports and validation."""

    _name = 'rn.gst.settings'
    _description = 'GST Pro Settings'
    _inherit = ['mail.thread']

    name = fields.Char(required=True, default='GST Settings')
    company_id = fields.Many2one(
        'res.company',
        required=True,
        default=lambda self: self.env.company,
    )
    gstin = fields.Char(string='GSTIN', tracking=True)
    pan = fields.Char(string='PAN')
    default_state_code = fields.Char(string='Default GST State Code')
    return_frequency = fields.Selection(
        selection=[
            ('month', 'Monthly'),
            ('quarter', 'Quarterly'),
        ],
        default='month',
        required=True,
    )
    json_version = fields.Char(string='JSON Version', default='GST3.1.6')
    financial_year = fields.Char(string='Current Financial Year')
    auto_validate = fields.Boolean(string='Auto Validate on Compute', default=True)
    auto_lock_after_export = fields.Boolean(default=False)
    active = fields.Boolean(default=True)

    _company_uniq = models.Constraint(
        'unique(company_id)',
        'Only one GST settings record per company.',
    )
