# -*- coding: utf-8 -*-
"""KPI registry and optional snapshot history."""

from odoo import fields, models


class RnDashboardKpi(models.Model):
    """Canonical KPI definition resolved by domain modules."""

    _name = 'rn.dashboard.kpi'
    _description = 'Dashboard KPI'
    _order = 'sequence, name'

    name = fields.Char(required=True)
    key = fields.Char(required=True, index=True)
    sequence = fields.Integer(default=10)
    active = fields.Boolean(default=True)
    domain = fields.Selection(
        selection=[
            ('generic', 'Generic'),
            ('mrp', 'Manufacturing'),
            ('sales', 'Sales'),
            ('quality', 'Quality'),
            ('maintenance', 'Maintenance'),
        ],
        default='generic',
        required=True,
        index=True,
    )
    unit = fields.Char()
    description = fields.Text()
    company_id = fields.Many2one(
        'res.company',
        default=lambda self: self.env.company,
        index=True,
    )

    _rn_dashboard_kpi_key_uniq = models.Constraint(
        'unique(key, company_id)',
        'KPI key must be unique per company.',
    )


class RnDashboardKpiSnapshot(models.Model):
    """Point-in-time KPI value for trends and exports."""

    _name = 'rn.dashboard.kpi.snapshot'
    _description = 'Dashboard KPI Snapshot'
    _order = 'snapshot_at desc, id desc'

    kpi_id = fields.Many2one('rn.dashboard.kpi', required=True, ondelete='cascade', index=True)
    kpi_key = fields.Char(related='kpi_id.key', store=True, index=True)
    snapshot_at = fields.Datetime(required=True, index=True, default=fields.Datetime.now)
    value = fields.Float(required=True)
    target = fields.Float()
    filter_id = fields.Many2one('rn.dashboard.filter')
    company_id = fields.Many2one(
        'res.company',
        required=True,
        default=lambda self: self.env.company,
        index=True,
    )
    note = fields.Char()
