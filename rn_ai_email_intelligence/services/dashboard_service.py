# -*- coding: utf-8 -*-
"""AI email dashboard metrics."""

import logging

from odoo import fields, models

_logger = logging.getLogger(__name__)


class RnAiEmailDashboardService(models.AbstractModel):
    _name = 'rn.ai.email.dashboard.service'
    _description = 'AI Email Dashboard Service'

    def get_dashboard_data(self, company_id=None):
        company_id = company_id or self.env.company.id
        domain = [('company_id', '=', company_id)]
        Draft = self.env['rn.ai.email.draft']
        settings = self.env['rn.ai.email.settings'].search(
            [('company_id', '=', company_id)], limit=1,
        )
        return {
            'cards': {
                'total_drafts': Draft.search_count(domain),
                'sent': Draft.search_count(domain + [('state', '=', 'sent')]),
                'review': Draft.search_count(domain + [('state', '=', 'review')]),
                'discarded': Draft.search_count(domain + [('state', '=', 'discarded')]),
                'credits': settings.credit_balance if settings else 0,
            },
            'updated_at': fields.Datetime.to_string(fields.Datetime.now()),
        }
