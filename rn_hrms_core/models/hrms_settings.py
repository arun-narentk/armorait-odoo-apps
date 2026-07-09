# -*- coding: utf-8 -*-
"""Company HRMS settings."""

from odoo import fields, models


class RnHrmsSettings(models.Model):
    """Core toggles shared by ARMORA HR companion modules."""

    _name = 'rn.hrms.settings'
    _description = 'HRMS Settings'
    _inherit = ['mail.thread']

    name = fields.Char(required=True, default='HRMS Settings')
    company_id = fields.Many2one(
        'res.company',
        required=True,
        default=lambda self: self.env.company,
    )
    enable_announcements = fields.Boolean(default=True)
    enable_approvals = fields.Boolean(default=True)
    enable_email = fields.Boolean(default=True)
    enable_whatsapp = fields.Boolean(default=False)
    enable_sms = fields.Boolean(default=False)
    employee_code_prefix = fields.Char(default='EMP')
    timezone = fields.Char(default='UTC')
    active = fields.Boolean(default=True)

    _company_uniq = models.Constraint(
        'unique(company_id)',
        'Only one HRMS settings record per company.',
    )
