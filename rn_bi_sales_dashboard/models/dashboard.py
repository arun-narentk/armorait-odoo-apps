# -*- coding: utf-8 -*-
"""Dashboard definition and layout."""

from odoo import fields, models


class RnBiSalesDashboard(models.Model):
    """Configurable sales dashboard container."""

    _name = 'rn.bi.sales.dashboard'
    _description = 'BI Sales Dashboard'
    _inherit = ['mail.thread']
    _order = 'sequence, name'

    name = fields.Char(required=True, tracking=True)
    sequence = fields.Integer(default=10)
    active = fields.Boolean(default=True)
    is_default = fields.Boolean(string='Default Dashboard')
    theme = fields.Selection(
        selection=[
            ('light', 'Light'),
            ('dark', 'Dark'),
            ('corporate', 'Corporate'),
        ],
        default='light',
    )
    refresh_interval = fields.Integer(
        string='Refresh Interval (seconds)',
        default=300,
        help='0 disables auto refresh.',
    )
    company_id = fields.Many2one(
        'res.company',
        required=True,
        default=lambda self: self.env.company,
    )
    widget_ids = fields.One2many('rn.bi.dashboard.widget', 'dashboard_id', string='Widgets')
    filter_id = fields.Many2one('rn.bi.dashboard.filter', string='Default Filter')
    favorite_ids = fields.One2many('rn.bi.dashboard.favorite', 'dashboard_id', string='Favorites')
    note = fields.Text()
