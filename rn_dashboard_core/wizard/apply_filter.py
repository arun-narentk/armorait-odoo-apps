# -*- coding: utf-8 -*-
"""Quick filter application that opens the dashboard shell."""

from odoo import fields, models


class RnDashboardApplyFilterWizard(models.TransientModel):
    _name = 'rn.dashboard.apply.filter.wizard'
    _description = 'Apply Dashboard Filter'

    dashboard_id = fields.Many2one('rn.dashboard', required=True)
    filter_id = fields.Many2one('rn.dashboard.filter', required=True)

    def action_open(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.client',
            'tag': 'rn_dashboard_core.shell',
            'name': self.dashboard_id.name,
            'params': {
                'dashboard_id': self.dashboard_id.id,
                'filter_id': self.filter_id.id,
            },
        }
