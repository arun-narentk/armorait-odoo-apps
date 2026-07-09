# -*- coding: utf-8 -*-
"""User-saved dashboard layouts and filters."""

from odoo import fields, models


class RnBiDashboardFavorite(models.Model):
    """Saved layout/filter combination for a user."""

    _name = 'rn.bi.dashboard.favorite'
    _description = 'BI Dashboard Favorite'
    _order = 'name'

    name = fields.Char(required=True)
    dashboard_id = fields.Many2one('rn.bi.sales.dashboard', required=True, ondelete='cascade')
    user_id = fields.Many2one('res.users', required=True, default=lambda self: self.env.user)
    filter_id = fields.Many2one('rn.bi.dashboard.filter')
    is_default = fields.Boolean()
    layout_json = fields.Text(help='Serialized widget order / visibility.')
    company_id = fields.Many2one(related='dashboard_id.company_id', store=True)
