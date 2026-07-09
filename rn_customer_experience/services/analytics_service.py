# -*- coding: utf-8 -*-
"""Track portal usage for business analytics."""

from odoo import models


class RnCustomerExperienceAnalyticsService(models.AbstractModel):
    _name = 'rn.customer.experience.analytics.service'
    _description = 'Customer Experience Analytics Service'

    def track_event(self, event_type, partner=None, description='', metadata=''):
        return self.env['rn.customer.experience.analytics'].sudo().create({
            'partner_id': partner.id if partner else False,
            'user_id': self.env.user.id,
            'company_id': self.env.company.id,
            'event_type': event_type,
            'description': description,
            'metadata': metadata,
        })

    def get_admin_dashboard(self):
        Analytics = self.env['rn.customer.experience.analytics']
        company = self.env.company
        events = Analytics.search([('company_id', '=', company.id)])
        logins = events.filtered(lambda e: e.event_type == 'login')
        payments = events.filtered(lambda e: e.event_type == 'payment')
        tickets = self.env['rn.customer.experience.ticket'].search([('company_id', '=', company.id)])
        partners = self.env['res.partner'].search([
            ('customer_rank', '>', 0),
            '|', ('company_id', '=', company.id), ('company_id', '=', False),
        ])
        return {
            'portal_logins': len(logins),
            'payment_actions': len(payments),
            'ticket_volume': len(tickets),
            'portal_partners': len(partners.filtered('user_ids')),
            'open_tickets': len(tickets.filtered(lambda t: t.state not in ('resolved', 'closed'))),
            'self_service_rate': round(
                len(events.filtered(lambda e: e.event_type in ('download', 'payment', 'ticket_create')))
                / max(len(events), 1) * 100,
                1,
            ),
        }
