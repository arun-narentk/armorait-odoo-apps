# -*- coding: utf-8 -*-
"""Reusable dashboard filter presets."""

from odoo import fields, models


class RnBiDashboardFilter(models.Model):
    """Stores date and dimensional filter presets for dashboards."""

    _name = 'rn.bi.dashboard.filter'
    _description = 'BI Dashboard Filter'
    _order = 'name'

    name = fields.Char(required=True)
    date_preset = fields.Selection(
        selection=[
            ('today', 'Today'),
            ('yesterday', 'Yesterday'),
            ('last_7', 'Last 7 Days'),
            ('last_30', 'Last 30 Days'),
            ('this_month', 'This Month'),
            ('last_month', 'Last Month'),
            ('quarter', 'This Quarter'),
            ('year', 'This Year'),
            ('custom', 'Custom Date'),
        ],
        default='this_month',
        required=True,
    )
    date_from = fields.Date()
    date_to = fields.Date()
    salesperson_ids = fields.Many2many('res.users', string='Salespersons')
    team_ids = fields.Many2many('crm.team', string='Sales Teams')
    partner_ids = fields.Many2many('res.partner', string='Customers')
    country_ids = fields.Many2many('res.country', string='Countries')
    product_ids = fields.Many2many('product.product', string='Products')
    categ_ids = fields.Many2many('product.category', string='Categories')
    company_id = fields.Many2one('res.company', default=lambda self: self.env.company)
    shared = fields.Boolean(string='Shareable', default=False)
