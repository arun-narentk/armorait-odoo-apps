# -*- coding: utf-8 -*-
"""Persisted dashboard KPI snapshots."""

from odoo import fields, models


class RnCrmDashboardSnapshot(models.Model):
    """Stores periodic KPI snapshots for charts and history."""

    _name = 'rn.crm.dashboard.snapshot'
    _description = 'CRM Dashboard Snapshot'
    _order = 'snapshot_date desc'

    name = fields.Char(required=True, default='Snapshot')
    snapshot_date = fields.Date(default=fields.Date.context_today, required=True)
    lead_count = fields.Integer()
    opportunity_count = fields.Integer()
    won_count = fields.Integer()
    lost_count = fields.Integer()
    revenue = fields.Float(digits=(16, 2))
    forecast = fields.Float(digits=(16, 2))
    company_id = fields.Many2one('res.company', required=True, default=lambda self: self.env.company)
