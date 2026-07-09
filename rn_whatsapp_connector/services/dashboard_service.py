# -*- coding: utf-8 -*-
"""WhatsApp KPI dashboard payload."""

from odoo import fields, models


class RnWhatsappDashboardService(models.AbstractModel):
    _name = 'rn.whatsapp.dashboard.service'
    _description = 'WhatsApp Dashboard Service'

    def get_dashboard_data(self, company_id=None):
        company_id = company_id or self.env.company.id
        Message = self.env['rn.whatsapp.message']
        domain = [('company_id', '=', company_id)]
        today = fields.Date.context_today(self)
        today_start = fields.Datetime.to_datetime(today)
        cards = {
            'sent': Message.search_count(domain + [('status', 'in', ['sent', 'delivered', 'read'])]),
            'delivered': Message.search_count(domain + [('status', '=', 'delivered')]),
            'read': Message.search_count(domain + [('status', '=', 'read')]),
            'failed': Message.search_count(domain + [('status', '=', 'failed')]),
            'queue_size': Message.search_count(domain + [('status', '=', 'queued')]),
            'today': Message.search_count(domain + [('create_date', '>=', today_start)]),
            'inbound': Message.search_count(domain + [('direction', '=', 'inbound')]),
            'accounts': self.env['rn.whatsapp.account'].search_count([
                ('company_id', '=', company_id), ('active', '=', True),
            ]),
        }
        total = cards['sent'] + cards['failed'] or 1
        cards['success_rate'] = round(100.0 * cards['sent'] / total, 1)
        sub = self.env['rn.whatsapp.subscription'].search([
            ('company_id', '=', company_id),
            ('state', 'in', ['trial', 'active']),
        ], limit=1)
        return {
            'cards': cards,
            'edition': sub.plan if sub else 'professional',
            'updated_at': fields.Datetime.to_string(fields.Datetime.now()),
        }
