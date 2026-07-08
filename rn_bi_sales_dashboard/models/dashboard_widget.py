# -*- coding: utf-8 -*-
"""Dashboard widgets (cards/charts/lists)."""

from odoo import fields, models


class RnBiDashboardWidget(models.Model):
    """A visual widget placed on a dashboard."""

    _name = 'rn.bi.dashboard.widget'
    _description = 'BI Dashboard Widget'
    _order = 'sequence, id'

    name = fields.Char(required=True)
    dashboard_id = fields.Many2one('rn.bi.sales.dashboard', required=True, ondelete='cascade', index=True)
    sequence = fields.Integer(default=10)
    widget_type = fields.Selection(
        selection=[
            ('kpi_card', 'KPI Card'),
            ('line_chart', 'Line Chart'),
            ('bar_chart', 'Bar Chart'),
            ('pie_chart', 'Pie Chart'),
            ('donut_chart', 'Donut Chart'),
            ('stacked_bar', 'Stacked Bar'),
            ('area_chart', 'Area Chart'),
            ('heatmap', 'Heatmap'),
            ('top_list', 'Top List'),
            ('table', 'Table'),
        ],
        required=True,
        default='kpi_card',
    )
    kpi_id = fields.Many2one('rn.bi.sales.kpi', string='KPI')
    chart_key = fields.Char(help='Chart dataset key used by chart_service.')
    width = fields.Selection(
        selection=[('3', '25%'), ('4', '33%'), ('6', '50%'), ('12', '100%')],
        default='4',
    )
    active = fields.Boolean(default=True)
    company_id = fields.Many2one(related='dashboard_id.company_id', store=True)
