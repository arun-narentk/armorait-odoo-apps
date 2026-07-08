# -*- coding: utf-8 -*-
"""Company CRM Ultimate Pro settings."""

from odoo import fields, models


class RnCrmSettings(models.Model):
    """Per-company scoring, duplicate, and prediction defaults."""

    _name = 'rn.crm.settings'
    _description = 'CRM Ultimate Pro Settings'
    _inherit = ['mail.thread']

    name = fields.Char(required=True, default='CRM Settings')
    company_id = fields.Many2one('res.company', required=True, default=lambda self: self.env.company)
    scoring_enabled = fields.Boolean(default=True)
    duplicate_sensitivity = fields.Selection(
        selection=[('strict', 'Strict'), ('balanced', 'Balanced'), ('loose', 'Loose')],
        default='balanced',
    )
    prediction_provider = fields.Selection(
        selection=[
            ('rule_engine', 'Rule Engine'),
            ('external', 'External AI Provider'),
        ],
        default='rule_engine',
    )
    reminder_interval_hours = fields.Integer(default=24)
    dashboard_refresh_minutes = fields.Integer(default=60)
    round_robin_assignment = fields.Boolean(default=False)
    active = fields.Boolean(default=True)

    _company_uniq = models.Constraint(
        'unique(company_id)',
        'Only one CRM Ultimate settings record per company.',
    )
