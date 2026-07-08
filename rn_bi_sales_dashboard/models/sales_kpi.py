# -*- coding: utf-8 -*-
"""Configurable KPI card definitions."""

from odoo import fields, models


class RnBiSalesKpi(models.Model):
    """One reusable KPI card configuration."""

    _name = 'rn.bi.sales.kpi'
    _description = 'BI Sales KPI'
    _order = 'sequence, id'

    name = fields.Char(required=True)
    code = fields.Char(required=True, index=True)
    sequence = fields.Integer(default=10)
    active = fields.Boolean(default=True)
    kpi_type = fields.Selection(
        selection=[
            ('today_sales', "Today's Sales"),
            ('yesterday_sales', 'Yesterday Sales'),
            ('weekly_sales', 'Weekly Sales'),
            ('monthly_sales', 'Monthly Sales'),
            ('quarterly_sales', 'Quarterly Sales'),
            ('yearly_sales', 'Yearly Sales'),
            ('total_revenue', 'Total Revenue'),
            ('gross_profit', 'Gross Profit'),
            ('margin', 'Margin %'),
            ('aov', 'Average Order Value'),
            ('orders', 'Orders'),
            ('customers', 'Customers'),
            ('new_customers', 'New Customers'),
            ('returning_customers', 'Returning Customers'),
            ('cancelled_orders', 'Cancelled Orders'),
            ('refunds', 'Refunds'),
            ('quotation_count', 'Quotation Count'),
            ('quotation_value', 'Quotation Value'),
            ('won_opportunities', 'Won Opportunities'),
            ('lost_opportunities', 'Lost Opportunities'),
        ],
        required=True,
    )
    card_size = fields.Selection(
        selection=[('sm', 'Small'), ('md', 'Medium'), ('lg', 'Large')],
        default='md',
    )
    color_theme = fields.Char(default='#4F46E5')
    refresh_interval = fields.Integer(default=300)
    company_id = fields.Many2one('res.company', default=lambda self: self.env.company)

    _code_company_uniq = models.Constraint(
        'unique(code, company_id)',
        'KPI code must be unique per company.',
    )
