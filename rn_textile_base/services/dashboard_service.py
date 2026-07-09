# -*- coding: utf-8 -*-
"""Textile operations dashboard."""

import logging

from odoo import fields, models

_logger = logging.getLogger(__name__)


class RnTextileDashboardService(models.AbstractModel):
    """Build Textile Manufacturing dashboard payload."""

    _name = 'rn.textile.dashboard.service'
    _description = 'Textile Dashboard Service'

    def get_dashboard_data(self, company_id=None):
        company_id = company_id or self.env.company.id
        domain = [('company_id', '=', company_id)]
        Machine = self.env['rn.textile.machine']
        util = self.env['rn.textile.factory.service'].get_machine_utilization_summary(company_id)
        return {
            'cards': {
                'factories': self.env['rn.textile.factory'].search_count(domain),
                'departments': self.env['rn.textile.department'].search_count(domain),
                'machines': util['total'],
                'active_machines': util['active'],
                'utilization_rate': util['utilization_rate'],
                'yarn_specs': self.env['rn.textile.yarn.spec'].search_count(domain + [('active', '=', True)]),
                'maintenance_machines': Machine.search_count(domain + [('state', '=', 'maintenance')]),
                'breakdown_machines': Machine.search_count(domain + [('state', '=', 'breakdown')]),
            },
            'machines_by_state': self._machines_by_state(company_id),
            'updated_at': fields.Datetime.to_string(fields.Datetime.now()),
        }

    def _machines_by_state(self, company_id):
        Machine = self.env['rn.textile.machine']
        result = []
        for state_key, state_label in Machine._fields['state'].selection:
            count = Machine.search_count([
                ('company_id', '=', company_id),
                ('active', '=', True),
                ('state', '=', state_key),
            ])
            if count:
                result.append({'state': state_key, 'label': state_label, 'count': count})
        return result
