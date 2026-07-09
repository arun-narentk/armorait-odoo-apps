# -*- coding: utf-8 -*-
"""Dashboard KPIs for document automation."""

from odoo import fields, models


class RnAiDocumentDashboardService(models.AbstractModel):
    _name = 'rn.ai.document.dashboard.service'
    _description = 'AI Document Dashboard Service'

    def get_dashboard_data(self, company_id=None):
        company_id = company_id or self.env.company.id
        Doc = self.env['rn.ai.document']
        domain = [('company_id', '=', company_id)]
        cards = {
            'generated': Doc.search_count(domain),
            'pending_approval': Doc.search_count(domain + [('state', '=', 'to_approve')]),
            'signed': Doc.search_count(domain + [('state', '=', 'signed')]),
            'final': Doc.search_count(domain + [('state', '=', 'final')]),
            'draft': Doc.search_count(domain + [('state', '=', 'draft')]),
            'templates': self.env['rn.ai.document.template'].search_count([
                ('company_id', '=', company_id), ('active', '=', True),
            ]),
            'types': self.env['rn.ai.document.type'].search_count([
                '|', ('company_id', '=', False), ('company_id', '=', company_id),
            ]),
        }
        sub = self.env['rn.ai.document.subscription'].search([
            ('company_id', '=', company_id),
            ('state', 'in', ['trial', 'active']),
        ], limit=1)
        return {
            'cards': cards,
            'edition': sub.plan if sub else 'marketplace',
            'updated_at': fields.Datetime.to_string(fields.Datetime.now()),
        }
