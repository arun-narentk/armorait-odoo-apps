# -*- coding: utf-8 -*-
"""Company temple settings."""

from odoo import fields, models


class RnTempleSettings(models.Model):
    """Defaults shared across temple companion modules."""

    _name = 'rn.temple.settings'
    _description = 'Temple Settings'
    _inherit = ['mail.thread']

    name = fields.Char(required=True, default='Temple Settings')
    company_id = fields.Many2one(
        'res.company',
        required=True,
        default=lambda self: self.env.company,
    )
    default_temple_id = fields.Many2one('rn.temple.temple', string='Default Temple')
    institution_label = fields.Char(
        default='Temple',
        help='UI label override: Temple, Church, Gurudwara, etc.',
    )
    devotee_label = fields.Char(default='Devotee')
    priest_label = fields.Char(default='Priest')
    enable_sms = fields.Boolean(default=False)
    enable_whatsapp = fields.Boolean(default=False)
    enable_email = fields.Boolean(default=True)
    enable_online_booking = fields.Boolean(default=True)
    enable_donation_portal = fields.Boolean(default=True)
    receipt_prefix = fields.Char(default='DN')
    seva_prefix = fields.Char(default='SV')
    timezone = fields.Char(default='Asia/Kolkata')
    active = fields.Boolean(default=True)

    _company_uniq = models.Constraint(
        'unique(company_id)',
        'Only one temple settings record per company.',
    )
