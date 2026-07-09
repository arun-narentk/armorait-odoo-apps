# -*- coding: utf-8 -*-
"""Customer AI conversations and transcript lines."""

from odoo import api, fields, models


class RnCustomerEngagementConversation(models.Model):
    _name = 'rn.customer.engagement.conversation'
    _description = 'Customer Engagement Conversation'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'write_date desc'

    name = fields.Char(required=True, copy=False, default='New', tracking=True)
    company_id = fields.Many2one('res.company', required=True, default=lambda self: self.env.company)
    channel_id = fields.Many2one('rn.customer.engagement.channel', required=True, ondelete='restrict')
    session_id = fields.Many2one('rn.customer.engagement.session', ondelete='set null')
    partner_id = fields.Many2one('res.partner', ondelete='set null')
    external_contact = fields.Char(required=True, index=True)
    topic = fields.Selection(
        [('order', 'Order Status'), ('invoice', 'Invoice'), ('payment', 'Payment'), ('delivery', 'Delivery'), ('stock', 'Stock'), ('support', 'Support'), ('general', 'General')],
        default='general', required=True, tracking=True,
    )
    state = fields.Selection([('bot', 'Bot'), ('escalated', 'Escalated'), ('closed', 'Closed')], default='bot', required=True, tracking=True)
    last_message = fields.Text()
    line_ids = fields.One2many('rn.customer.engagement.line', 'conversation_id')
    escalation_id = fields.Many2one('rn.customer.engagement.escalation', ondelete='set null')

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', 'New') == 'New':
                vals['name'] = self.env['ir.sequence'].next_by_code('rn.customer.engagement.conversation') or 'New'
        return super().create(vals_list)

    def post_line(self, direction, body, actor_name='Assistant'):
        self.ensure_one()
        line = self.env['rn.customer.engagement.line'].create({
            'conversation_id': self.id,
            'direction': direction,
            'content': body,
            'actor_name': actor_name,
        })
        self.write({'last_message': body})
        return line


class RnCustomerEngagementLine(models.Model):
    _name = 'rn.customer.engagement.line'
    _description = 'Customer Engagement Transcript Line'
    _order = 'create_date asc'

    conversation_id = fields.Many2one('rn.customer.engagement.conversation', required=True, ondelete='cascade')
    company_id = fields.Many2one(related='conversation_id.company_id', store=True, readonly=True)
    direction = fields.Selection([('inbound', 'Inbound'), ('outbound', 'Outbound')], required=True, default='inbound')
    actor_name = fields.Char(default='Assistant')
    content = fields.Text(required=True)
