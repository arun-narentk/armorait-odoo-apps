# -*- coding: utf-8 -*-
"""Approval dashboard KPIs."""

import logging

from odoo import fields, models

_logger = logging.getLogger(__name__)


class RnApprovalDashboardService(models.AbstractModel):
    """Dashboard metrics for approval engine."""

    _name = 'rn.approval.dashboard.service'
    _description = 'Approval Dashboard Service'

    def get_dashboard_data(self, company_id=None):
        company_id = company_id or self.env.company.id
        domain = [('company_id', '=', company_id)]
        Request = self.env['rn.approval.request']
        pending = Request.search(domain + [('state', '=', 'pending')])
        return {
            'cards': {
                'pending': Request.search_count(domain + [('state', '=', 'pending')]),
                'approved': Request.search_count(domain + [('state', '=', 'approved')]),
                'rejected': Request.search_count(domain + [('state', '=', 'rejected')]),
                'overdue': len(pending.filtered('is_overdue')),
                'my_pending': Request.search_count(
                    domain + [
                        ('state', '=', 'pending'),
                        ('line_ids.user_id', '=', self.env.user.id),
                        ('line_ids.state', '=', 'pending'),
                    ]
                ),
            },
            'updated_at': fields.Datetime.to_string(fields.Datetime.now()),
        }
