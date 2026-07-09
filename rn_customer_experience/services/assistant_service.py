# -*- coding: utf-8 -*-
"""Keyword-based customer assistant (Phase 3 foundation)."""

from odoo import models


class RnCustomerExperienceAssistantService(models.AbstractModel):
    _name = 'rn.customer.experience.assistant.service'
    _description = 'Customer Experience Assistant Service'

    def answer_query(self, partner, query: str):
        query_lower = (query or '').lower().strip()
        dashboard = self.env['rn.customer.experience.dashboard.service'].get_partner_dashboard(
            partner,
        )
        if not query_lower:
            return {
                'answer': 'Ask about your orders, invoices, AMC, warranty, or service tickets.',
                'action': False,
            }
        if 'invoice' in query_lower or 'bill' in query_lower:
            count = dashboard['summary']['outstanding_invoices']
            amount = dashboard['summary']['outstanding_amount']
            return {
                'answer': f'You have {count} outstanding invoice(s) totaling {amount:.2f}.',
                'action': {'url': '/my/experience/invoices'},
            }
        if 'order' in query_lower or 'where is' in query_lower:
            orders = dashboard['orders'][:1]
            if orders:
                return {
                    'answer': f'Latest order {orders[0]["name"]} is {orders[0]["state"]}.',
                    'action': {'url': '/my/experience/orders'},
                }
            return {'answer': 'No recent orders found.', 'action': {'url': '/my/experience/orders'}}
        if 'amc' in query_lower or 'maintenance' in query_lower:
            amcs = dashboard['amcs']
            if amcs:
                return {
                    'answer': f'Next AMC renewal: {amcs[0]["renewal_date"] or "not set"}.',
                    'action': {'url': '/my/experience/amc'},
                }
            return {'answer': 'No active AMC contracts found.', 'action': {'url': '/my/experience/amc'}}
        if 'warranty' in query_lower:
            count = dashboard['summary']['active_warranties']
            return {
                'answer': f'You have {count} active warranty record(s).',
                'action': {'url': '/my/experience/warranty'},
            }
        if 'ticket' in query_lower or 'service' in query_lower or 'book' in query_lower:
            return {
                'answer': 'You can raise a service ticket from the Support section.',
                'action': {'url': '/my/experience/tickets/new'},
            }
        if 'download' in query_lower:
            return {
                'answer': 'Open Downloads to access invoices, manuals, and certificates.',
                'action': {'url': '/my/experience/downloads'},
            }
        return {
            'answer': 'I can help with orders, invoices, payments, warranty, AMC, and support tickets.',
            'action': {'url': '/my/experience'},
        }
