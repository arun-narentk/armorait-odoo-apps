# -*- coding: utf-8 -*-
"""Real estate operations dashboard."""

import logging

from odoo import fields, models

_logger = logging.getLogger(__name__)


class RnRealestateDashboardService(models.AbstractModel):
    """Build Real Estate ERP dashboard payload."""

    _name = 'rn.realestate.dashboard.service'
    _description = 'Real Estate Dashboard Service'

    def get_dashboard_data(self, company_id=None):
        company_id = company_id or self.env.company.id
        domain = [('company_id', '=', company_id)]
        Lead = self.env['rn.realestate.lead']
        inventory = self.env['rn.realestate.developer.service'].get_inventory_summary(company_id)
        active_leads = Lead.search_count(domain + [('stage', 'not in', ('booked', 'lost'))])
        return {
            'cards': {
                'developers': self.env['rn.realestate.developer'].search_count(domain),
                'projects': self.env['rn.realestate.project'].search_count(domain),
                'total_units': inventory['total'],
                'available_units': inventory['available'],
                'booked_units': inventory['booked'],
                'sold_units': inventory['sold'],
                'active_leads': active_leads,
                'sell_through': inventory['sell_through'],
            },
            'pipeline': self._lead_pipeline(company_id),
            'updated_at': fields.Datetime.to_string(fields.Datetime.now()),
        }

    def _lead_pipeline(self, company_id):
        Lead = self.env['rn.realestate.lead']
        result = []
        for stage_key, stage_label in Lead._fields['stage'].selection:
            count = Lead.search_count([
                ('company_id', '=', company_id),
                ('stage', '=', stage_key),
            ])
            if count:
                result.append({'stage': stage_key, 'label': stage_label, 'count': count})
        return result
