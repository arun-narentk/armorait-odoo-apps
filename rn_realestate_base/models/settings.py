# -*- coding: utf-8 -*-
"""Company real estate settings."""

from odoo import fields, models


class RnRealestateSettings(models.Model):
    """Defaults shared across real estate companion modules."""

    _name = 'rn.realestate.settings'
    _description = 'Real Estate Settings'
    _inherit = ['mail.thread']

    name = fields.Char(required=True, default='Real Estate Settings')
    company_id = fields.Many2one(
        'res.company',
        required=True,
        default=lambda self: self.env.company,
    )
    default_developer_id = fields.Many2one('rn.realestate.developer', string='Default Developer')
    developer_label = fields.Char(default='Builder')
    enable_portal = fields.Boolean(default=True)
    enable_whatsapp = fields.Boolean(default=False)
    enable_site_visit = fields.Boolean(default=True)
    enable_commission = fields.Boolean(default=True)
    booking_prefix = fields.Char(default='BKG')
    receipt_prefix = fields.Char(default='RCP')
    token_amount_default = fields.Monetary(currency_field='currency_id')
    currency_id = fields.Many2one(
        'res.currency',
        default=lambda self: self.env.company.currency_id,
    )
    active = fields.Boolean(default=True)

    _company_uniq = models.Constraint(
        'unique(company_id)',
        'Only one real estate settings record per company.',
    )
