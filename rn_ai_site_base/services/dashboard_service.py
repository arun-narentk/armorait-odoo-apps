# -*- coding: utf-8 -*-
"""AI site builder dashboard."""

import logging

from odoo import fields, models

_logger = logging.getLogger(__name__)


class RnAiSiteDashboardService(models.AbstractModel):
    """Dashboard KPIs for AI Business Launch."""

    _name = 'rn.ai.site.dashboard.service'
    _description = 'AI Site Dashboard Service'

    def get_dashboard_data(self, company_id=None):
        company_id = company_id or self.env.company.id
        domain = [('company_id', '=', company_id)]
        Brief = self.env['rn.ai.site.brief']
        Site = self.env['rn.ai.site.site']
        settings = self.env['rn.ai.site.brief.service'].ensure_default_settings(company_id)
        return {
            'cards': {
                'briefs': Brief.search_count(domain),
                'sites': Site.search_count(domain),
                'published': Site.search_count(domain + [('state', '=', 'published')]),
                'ready': Site.search_count(domain + [('state', '=', 'ready')]),
                'draft_briefs': Brief.search_count(domain + [('state', '=', 'draft')]),
                'ai_credits': settings.credit_balance,
            },
            'recent_briefs': self._recent_briefs(company_id),
            'updated_at': fields.Datetime.to_string(fields.Datetime.now()),
        }

    def _recent_briefs(self, company_id):
        briefs = self.env['rn.ai.site.brief'].search(
            [('company_id', '=', company_id)],
            order='create_date desc',
            limit=5,
        )
        return [{
            'id': b.id,
            'name': b.name,
            'business_name': b.business_name,
            'state': b.state,
            'location': b.location or '',
        } for b in briefs]
