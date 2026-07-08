# -*- coding: utf-8 -*-
"""Wizard to open dashboard with a specific filter preset."""

from odoo import fields, models


class RnBiSalesFilterWizard(models.TransientModel):
    """Capture filter values then open the dashboard client action."""

    _name = 'rn.bi.sales.filter.wizard'
    _description = 'BI Sales Filter Wizard'

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

    def action_open_dashboard(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.client',
            'tag': 'rn_bi_sales_dashboard.dashboard',
            'context': {
                'bi_filters': {
                    'date_preset': self.date_preset,
                    'date_from': self.date_from,
                    'date_to': self.date_to,
                    'salesperson_ids': self.salesperson_ids.ids,
                    'team_ids': self.team_ids.ids,
                },
            },
        }
