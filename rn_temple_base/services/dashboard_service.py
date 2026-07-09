# -*- coding: utf-8 -*-
"""Temple operations dashboard."""

import logging
from datetime import timedelta

from odoo import fields, models

_logger = logging.getLogger(__name__)


class RnTempleDashboardService(models.AbstractModel):
    """Build Temple Management dashboard payload."""

    _name = 'rn.temple.dashboard.service'
    _description = 'Temple Dashboard Service'

    def get_dashboard_data(self, company_id=None):
        company_id = company_id or self.env.company.id
        today = fields.Date.context_today(self)
        end = today + timedelta(days=30)
        Temple = self.env['rn.temple.temple']
        Festival = self.env['rn.temple.festival']
        domain = [('company_id', '=', company_id)]
        upcoming = Festival.search_count(domain + [
            ('date_start', '>=', today),
            ('date_start', '<=', end),
            ('state', '!=', 'cancelled'),
        ])
        return {
            'cards': {
                'temples': Temple.search_count(domain),
                'branches': self.env['rn.temple.branch'].search_count(domain),
                'trustees': self.env['rn.temple.trustee'].search_count(domain + [('active', '=', True)]),
                'priests': self.env['rn.temple.priest'].search_count(domain + [('active', '=', True)]),
                'upcoming_festivals': upcoming,
                'departments': self.env['rn.temple.department'].search_count(domain),
            },
            'festivals': self.env['rn.temple.festival.service'].get_upcoming_festivals(
                company_id=company_id,
                days=60,
                limit=10,
            ),
            'updated_at': fields.Datetime.to_string(fields.Datetime.now()),
        }
