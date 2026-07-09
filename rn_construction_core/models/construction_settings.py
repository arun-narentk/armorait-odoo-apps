# -*- coding: utf-8 -*-

from odoo import fields, models


class RnConstructionSettings(models.Model):
    _name = 'rn.construction.settings'
    _description = 'Construction Settings'
    _rec_name = 'company_id'

    company_id = fields.Many2one('res.company', required=True, ondelete='cascade', index=True)
    default_retention_pct = fields.Float(default=5.0)
    require_boq_approval = fields.Boolean(default=True)
    ai_cost_prediction = fields.Boolean(default=True)
    ai_daily_summary = fields.Boolean(default=True)
    _sql_constraints = [
        ('company_uniq', 'unique(company_id)', 'Only one construction settings record per company.'),
    ]
