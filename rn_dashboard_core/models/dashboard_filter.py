# -*- coding: utf-8 -*-
"""Reusable filter presets for dashboards."""

from odoo import fields, models


class RnDashboardFilter(models.Model):
    """Saved filter context passed into dashboard payload builders."""

    _name = 'rn.dashboard.filter'
    _description = 'Dashboard Filter'
    _order = 'name'

    name = fields.Char(required=True)
    active = fields.Boolean(default=True)
    date_preset = fields.Selection(
        selection=[
            ('today', 'Today'),
            ('yesterday', 'Yesterday'),
            ('last_7', 'Last 7 Days'),
            ('last_30', 'Last 30 Days'),
            ('this_month', 'This Month'),
            ('last_month', 'Last Month'),
            ('this_quarter', 'This Quarter'),
            ('this_year', 'This Year'),
            ('custom', 'Custom'),
        ],
        default='today',
        required=True,
    )
    date_from = fields.Date()
    date_to = fields.Date()
    plant = fields.Char(string='Plant / Site')
    warehouse = fields.Char()
    production_line = fields.Char(string='Production Line')
    work_center = fields.Char(string='Work Center')
    machine = fields.Char()
    product = fields.Char()
    category = fields.Char()
    shift = fields.Selection(
        selection=[
            ('morning', 'Morning'),
            ('evening', 'Evening'),
            ('night', 'Night'),
            ('all', 'All Shifts'),
        ],
        default='all',
    )
    team = fields.Char()
    operator = fields.Char()
    company_id = fields.Many2one(
        'res.company',
        required=True,
        default=lambda self: self.env.company,
        index=True,
    )
    note = fields.Text()

    def to_vals(self):
        self.ensure_one()
        return {
            'date_preset': self.date_preset,
            'date_from': self.date_from,
            'date_to': self.date_to,
            'plant': self.plant,
            'warehouse': self.warehouse,
            'production_line': self.production_line,
            'work_center': self.work_center,
            'machine': self.machine,
            'product': self.product,
            'category': self.category,
            'shift': self.shift,
            'team': self.team,
            'operator': self.operator,
            'company_id': self.company_id.id,
        }
