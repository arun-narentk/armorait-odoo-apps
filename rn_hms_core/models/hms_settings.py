# -*- coding: utf-8 -*-
"""Company HMS settings."""

from odoo import fields, models


class RnHmsSettings(models.Model):
    """Defaults shared across hospital companion modules."""

    _name = 'rn.hms.settings'
    _description = 'HMS Settings'
    _inherit = ['mail.thread']

    name = fields.Char(required=True, default='Hospital Settings')
    company_id = fields.Many2one(
        'res.company',
        required=True,
        default=lambda self: self.env.company,
    )
    patient_code_prefix = fields.Char(default='P')
    default_slot_minutes = fields.Integer(default=15)
    enable_sms = fields.Boolean(default=False)
    enable_whatsapp = fields.Boolean(default=False)
    enable_email = fields.Boolean(default=True)
    enable_token = fields.Boolean(default=True)
    timezone = fields.Char(default='UTC')
    active = fields.Boolean(default=True)

    _company_uniq = models.Constraint(
        'unique(company_id)',
        'Only one HMS settings record per company.',
    )
