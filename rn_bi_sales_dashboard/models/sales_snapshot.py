# -*- coding: utf-8 -*-
"""Materialized KPI snapshots for performance."""

from odoo import fields, models


class RnBiSalesSnapshot(models.Model):
    """Stores aggregated sales KPIs for fast dashboard loads."""

    _name = 'rn.bi.sales.snapshot'
    _description = 'BI Sales Snapshot'
    _order = 'snapshot_date desc, id desc'

    name = fields.Char(required=True, default='Sales Snapshot')
    snapshot_date = fields.Date(required=True, default=fields.Date.context_today, index=True)
    period_key = fields.Char(index=True, help='today/week/month/quarter/year/custom key')
    revenue = fields.Float(digits=(16, 2))
    orders = fields.Integer()
    quotations = fields.Integer()
    quotation_value = fields.Float(digits=(16, 2))
    customers = fields.Integer()
    new_customers = fields.Integer()
    margin = fields.Float(digits=(16, 2))
    aov = fields.Float(string='Average Order Value', digits=(16, 2))
    won_opportunities = fields.Integer()
    lost_opportunities = fields.Integer()
    company_id = fields.Many2one('res.company', required=True, default=lambda self: self.env.company, index=True)
    payload = fields.Text(help='Optional JSON extras for charts.')
