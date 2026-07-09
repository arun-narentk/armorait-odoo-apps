# -*- coding: utf-8 -*-
"""Customer conversation thread per connector."""

from odoo import api, fields, models
from odoo.exceptions import UserError


class RnMessagingConversation(models.Model):
    _name = 'rn.messaging.conversation'
    _description = 'Messaging Conversation'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'last_message_at desc, id desc'

    name = fields.Char(required=True, tracking=True)
    connector_id = fields.Many2one(
        'rn.messaging.connector',
        required=True,
        ondelete='restrict',
        index=True,
    )
    company_id = fields.Many2one(
        related='connector_id.company_id',
        store=True,
        index=True,
    )
    partner_id = fields.Many2one('res.partner', index=True, tracking=True)
    external_contact_id = fields.Char(
        string='External Contact ID',
        index=True,
        help='Channel-specific user identifier such as WhatsApp wa_id.',
    )
    channel_type = fields.Selection(related='connector_id.channel_type', store=True)
    state = fields.Selection(
        selection=[
            ('open', 'Open'),
            ('bot', 'Bot Active'),
            ('human', 'Human Agent'),
            ('closed', 'Closed'),
        ],
        default='bot',
        tracking=True,
    )
    bot_session_id = fields.Many2one('rn.messaging.bot.session', ondelete='set null')
    lead_id = fields.Many2one('crm.lead', string='CRM Lead', tracking=True)
    message_ids = fields.One2many('rn.messaging.message', 'conversation_id')
    message_count = fields.Integer(compute='_compute_message_count')
    last_message_preview = fields.Char(compute='_compute_last_message_preview')
    last_message_at = fields.Datetime(index=True)

    @api.depends('message_ids')
    def _compute_message_count(self):
        grouped = self.env['rn.messaging.message'].read_group(
            [('conversation_id', 'in', self.ids)],
            ['conversation_id'],
            ['conversation_id'],
        )
        counts = {row['conversation_id'][0]: row['conversation_id_count'] for row in grouped}
        for conversation in self:
            conversation.message_count = counts.get(conversation.id, 0)

    @api.depends('message_ids.content', 'message_ids.create_date')
    def _compute_last_message_preview(self):
        for conversation in self:
            last = conversation.message_ids.sorted('create_date', reverse=True)[:1]
            preview = (last.content or '')[:120]
            conversation.last_message_preview = preview

    def action_open_messages(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Messages',
            'res_model': 'rn.messaging.message',
            'view_mode': 'list,form',
            'domain': [('conversation_id', '=', self.id)],
            'context': {'default_conversation_id': self.id},
        }

    def action_create_lead(self):
        self.ensure_one()
        lead = self._create_lead_record()
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'crm.lead',
            'res_id': lead.id,
            'view_mode': 'form',
        }

    def _create_lead_record(self):
        self.ensure_one()
        if self.lead_id:
            return self.lead_id
        lead = self.env['crm.lead'].create({
            'name': self.name,
            'partner_id': self.partner_id.id,
            'description': self.last_message_preview,
            'company_id': self.company_id.id,
        })
        self.lead_id = lead.id
        return lead

    def action_handoff_human(self):
        self.write({'state': 'human'})
        if self.bot_session_id:
            self.bot_session_id.write({'state': 'handoff'})

    def action_open_reply_wizard(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Send Reply',
            'res_model': 'rn.messaging.compose.reply.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_conversation_id': self.id},
        }

    def get_inbox_chat_data(self):
        self.ensure_one()
        templates = self.env['rn.messaging.template'].search([
            ('active', '=', True),
            '|',
            ('connector_id', '=', False),
            ('connector_id', '=', self.connector_id.id),
        ], limit=50)
        return {
            'conversation': {
                'id': self.id,
                'name': self.name,
                'state': self.state,
                'channel_type': self.channel_type,
                'partner_name': self.partner_id.name or '',
            },
            'messages': [
                {
                    'id': message.id,
                    'direction': message.direction,
                    'content': message.content,
                    'create_date': fields.Datetime.to_string(message.create_date),
                    'delivery_state': message.delivery_state,
                }
                for message in self.message_ids.sorted('create_date')
            ],
            'templates': [
                {'id': template.id, 'name': template.name}
                for template in templates
            ],
        }

    def post_agent_reply(self, body, template_id=False):
        self.ensure_one()
        text = (body or '').strip()
        template = self.env['rn.messaging.template']
        if template_id:
            template = template.browse(template_id)
            if template.exists():
                text = template.render_body(partner=self.partner_id, conversation=self)
        if not text:
            raise UserError('Please enter a message before sending.')
        if self.state == 'closed':
            raise UserError('This conversation is closed.')
        if self.state == 'bot':
            self.action_handoff_human()
        queue = self.env['rn.messaging.queue.service']
        message = queue.enqueue_text(self, text, priority=20)
        if template_id and template.exists():
            message.template_id = template.id
        queue.deliver_message(message)
        return self.get_inbox_chat_data()
