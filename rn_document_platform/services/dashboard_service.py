# -*- coding: utf-8 -*-
"""Document platform dashboard."""

import logging

from odoo import fields, models

_logger = logging.getLogger(__name__)


class RnDocDashboardService(models.AbstractModel):
    _name = 'rn.doc.dashboard.service'
    _description = 'Document Platform Dashboard Service'

    def get_dashboard_data(self, company_id=None):
        company_id = company_id or self.env.company.id
        domain = [('company_id', '=', company_id)]
        Request = self.env['rn.doc.sign.request']
        settings = self.env['rn.doc.platform.settings'].search(
            [('company_id', '=', company_id)], limit=1,
        )
        high_risk = self.env['rn.doc.ai.analysis'].search_count(
            domain + [('risk_level', '=', 'high')],
        )
        return {
            'cards': {
                'pending': Request.search_count(domain + [('state', 'in', ('sent', 'partial'))]),
                'completed': Request.search_count(domain + [('state', '=', 'completed')]),
                'declined': Request.search_count(domain + [('state', '=', 'declined')]),
                'draft': Request.search_count(domain + [('state', '=', 'draft')]),
                'high_risk': high_risk,
                'credits': settings.signature_credit_balance if settings else 0,
            },
            'updated_at': fields.Datetime.to_string(fields.Datetime.now()),
        }
