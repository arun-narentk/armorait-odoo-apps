# -*- coding: utf-8 -*-
"""Company workforce intelligence settings."""

from odoo import fields, models


class RnHrIntelligenceSettings(models.Model):
    """Per-company HR intelligence configuration."""

    _name = 'rn.hr.intelligence.settings'
    _description = 'HR Intelligence Settings'
    _inherit = ['mail.thread']

    name = fields.Char(default='Workforce Intelligence Settings', required=True)
    company_id = fields.Many2one(
        'res.company',
        required=True,
        default=lambda self: self.env.company,
    )
    enable_ai_summary = fields.Boolean(default=True)
    enable_anomaly_detection = fields.Boolean(default=True)
    overtime_threshold_hours = fields.Float(default=48.0, string='Monthly OT Alert (hours)')
    pf_rate = fields.Float(default=12.0, string='PF Rate %')
    esi_rate = fields.Float(default=3.25, string='ESI Rate %')
    dashboard_refresh_seconds = fields.Integer(default=120)
    active = fields.Boolean(default=True)

    _company_uniq = models.Constraint(
        'unique(company_id)',
        'Only one HR intelligence settings record per company.',
    )
