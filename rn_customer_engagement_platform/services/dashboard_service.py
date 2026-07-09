# -*- coding: utf-8 -*-
"""Dashboard metrics for customer engagement operations."""

from odoo import models


class RnCustomerEngagementDashboardService(models.AbstractModel):
    _name = 'rn.customer.engagement.dashboard.service'
    _description = 'Customer Engagement Dashboard Service'

    def get_dashboard_data(self):
        channels = self.env['rn.customer.engagement.channel'].search([], limit=20)
        conversations = self.env['rn.customer.engagement.conversation'].search([], order='create_date desc', limit=10)
        escalations = self.env['rn.customer.engagement.escalation'].search([], order='create_date desc', limit=10)
        return {
            'channels': self.env['rn.customer.engagement.channel'].search_count([]),
            'authenticated_sessions': self.env['rn.customer.engagement.session'].search_count([('auth_state', '=', 'authenticated')]),
            'active_conversations': self.env['rn.customer.engagement.conversation'].search_count([('state', '!=', 'closed')]),
            'open_escalations': self.env['rn.customer.engagement.escalation'].search_count([('state', '!=', 'resolved')]),
            'knowledge_articles': self.env['rn.customer.engagement.knowledge'].search_count([('active', '=', True)]),
            'channel_mix': [{'id': c.id, 'name': c.name, 'type': c.channel_type, 'auth': c.authentication_mode} for c in channels],
            'recent_conversations': [{'id': c.id, 'name': c.name, 'topic': c.topic, 'state': c.state, 'last_message': c.last_message or ''} for c in conversations],
            'recent_escalations': [{'id': e.id, 'name': e.name, 'category': e.category, 'state': e.state, 'summary': e.summary} for e in escalations],
        }
