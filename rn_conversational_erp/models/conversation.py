# -*- coding: utf-8 -*-
"""Conversation threads and messages."""

from odoo import api, fields, models


class RnConversationalErpConversation(models.Model):
    _name = 'rn.conversational.erp.conversation'
    _description = 'Conversational ERP Conversation'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'write_date desc'

    name = fields.Char(required=True, copy=False, default='New', tracking=True)
    company_id = fields.Many2one('res.company', required=True, default=lambda self: self.env.company)
    channel_id = fields.Many2one('rn.conversational.erp.channel', required=True, ondelete='restrict')
    assistant_id = fields.Many2one('rn.conversational.erp.assistant', ondelete='set null')
    partner_id = fields.Many2one('res.partner')
    user_id = fields.Many2one('res.users')
    external_contact_id = fields.Char(required=True, index=True)
    intent = fields.Selection(
        selection=[
            ('approval', 'Approval'),
            ('sales', 'Sales'),
            ('inventory', 'Inventory'),
            ('hr', 'HR'),
            ('executive', 'Executive'),
            ('support', 'Support'),
            ('general', 'General'),
        ],
        default='general',
        tracking=True,
    )
    state = fields.Selection(
        [('bot', 'Bot'), ('human', 'Human'), ('closed', 'Closed')],
        default='bot',
        tracking=True,
    )
    last_message = fields.Text()
    line_ids = fields.One2many('rn.conversational.erp.message', 'conversation_id')
    approval_ids = fields.One2many('rn.conversational.erp.approval', 'conversation_id')

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', 'New') == 'New':
                vals['name'] = self.env['ir.sequence'].next_by_code('rn.conversational.erp.conversation') or 'New'
        return super().create(vals_list)

    def post_message(self, direction, body, actor_name='System'):
        self.ensure_one()
        message = self.env['rn.conversational.erp.message'].create({
            'conversation_id': self.id,
            'direction': direction,
            'content': body,
            'actor_name': actor_name,
        })
        self.write({'last_message': body})
        return message


class RnConversationalErpMessage(models.Model):
    _name = 'rn.conversational.erp.message'
    _description = 'Conversational ERP Message'
    _order = 'create_date asc'

    conversation_id = fields.Many2one('rn.conversational.erp.conversation', required=True, ondelete='cascade')
    company_id = fields.Many2one(related='conversation_id.company_id', store=True, readonly=True)
    direction = fields.Selection([('inbound', 'Inbound'), ('outbound', 'Outbound')], required=True, default='inbound')
    content = fields.Text(required=True)
    actor_name = fields.Char(default='System')
