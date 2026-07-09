# -*- coding: utf-8 -*-
"""Backend dashboard for conversational ERP operations."""

from odoo import models


class RnConversationalErpDashboardService(models.AbstractModel):
    _name = 'rn.conversational.erp.dashboard.service'
    _description = 'Conversational ERP Dashboard Service'

    def get_dashboard_data(self):
        channels = self.env['rn.conversational.erp.channel'].search([], limit=20)
        conversations = self.env['rn.conversational.erp.conversation'].search([], order='create_date desc', limit=10)
        approvals = self.env['rn.conversational.erp.approval'].search([], order='create_date desc', limit=10)
        return {
            'channels': self.env['rn.conversational.erp.channel'].search_count([]),
            'connected_channels': self.env['rn.conversational.erp.channel'].search_count([('status', '=', 'connected')]),
            'open_conversations': self.env['rn.conversational.erp.conversation'].search_count([('state', '!=', 'closed')]),
            'pending_approvals': self.env['rn.conversational.erp.approval'].search_count([('state', '=', 'pending')]),
            'assistant_count': self.env['rn.conversational.erp.assistant'].search_count([('active', '=', True)]),
            'channel_mix': [{
                'id': channel.id,
                'name': channel.name,
                'type': channel.channel_type,
                'status': channel.status,
            } for channel in channels],
            'recent_conversations': [{
                'id': conv.id,
                'name': conv.name,
                'intent': conv.intent,
                'channel': conv.channel_id.name,
                'last_message': conv.last_message or '',
            } for conv in conversations],
            'recent_approvals': [{
                'id': approval.id,
                'name': approval.name,
                'state': approval.state,
                'summary': approval.summary,
            } for approval in approvals],
        }
