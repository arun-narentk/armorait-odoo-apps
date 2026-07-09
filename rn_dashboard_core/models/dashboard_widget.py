# -*- coding: utf-8 -*-
"""Configurable widget placement on a dashboard."""

from odoo import fields, models


class RnDashboardWidget(models.Model):
    """Widget card bound to a KPI key or chart series."""

    _name = 'rn.dashboard.widget'
    _description = 'Dashboard Widget'
    _order = 'sequence, id'

    name = fields.Char(required=True)
    sequence = fields.Integer(default=10)
    active = fields.Boolean(default=True)
    dashboard_id = fields.Many2one('rn.dashboard', required=True, ondelete='cascade', index=True)
    widget_type = fields.Selection(
        selection=[
            ('kpi_card', 'KPI Card'),
            ('gauge', 'Gauge'),
            ('line', 'Line Chart'),
            ('bar', 'Bar Chart'),
            ('area', 'Area Chart'),
            ('pie', 'Pie Chart'),
            ('pareto', 'Pareto Chart'),
            ('heatmap', 'Heat Map'),
            ('timeline', 'Timeline'),
            ('status_grid', 'Status Grid'),
            ('alert_list', 'Alert List'),
            ('table', 'Data Table'),
            ('message', 'Message / Banner'),
        ],
        required=True,
        default='kpi_card',
    )
    kpi_key = fields.Char(
        string='KPI Key',
        help='Stable key resolved by domain modules (e.g. mrp.oee, mrp.scrap_pct).',
        index=True,
    )
    size = fields.Selection(
        selection=[
            ('s', 'Small'),
            ('m', 'Medium'),
            ('l', 'Large'),
            ('xl', 'Extra Large'),
        ],
        default='m',
        required=True,
    )
    color = fields.Char(default='#0F766E')
    threshold_warn = fields.Float(string='Warn Threshold')
    threshold_crit = fields.Float(string='Critical Threshold')
    config_json = fields.Text(
        string='Advanced Config (JSON)',
        help='Optional JSON for series labels, units, or provider options.',
    )
    company_id = fields.Many2one(
        related='dashboard_id.company_id',
        store=True,
        index=True,
    )
