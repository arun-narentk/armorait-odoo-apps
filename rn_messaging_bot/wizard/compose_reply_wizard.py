# -*- coding: utf-8 -*-
"""Agent reply composer wizard."""

from odoo import api, fields, models
from odoo.exceptions import UserError


class RnMessagingComposeReplyWizard(models.TransientModel):
    _name = 'rn.messaging.compose.reply.wizard'
    _description = 'Compose Agent Reply'

    conversation_id = fields.Many2one(
        'rn.messaging.conversation',
        required=True,
        ondelete='cascade',
    )
    body = fields.Text(string='Message', required=True)

    @api.model
    def default_get(self, fields_list):
        vals = super().default_get(fields_list)
        conversation_id = self.env.context.get('default_conversation_id')
        if conversation_id:
            vals['conversation_id'] = conversation_id
        return vals

    def action_send(self):
        self.ensure_one()
        if not self.body.strip():
            raise UserError('Please enter a message before sending.')
        conversation = self.conversation_id
        if conversation.state == 'closed':
            raise UserError('This conversation is closed.')
        if conversation.state == 'bot':
            conversation.action_handoff_human()
        queue = self.env['rn.messaging.queue.service']
        message = queue.enqueue_text(conversation, self.body.strip(), priority=20)
        queue.deliver_message(message)
        return {'type': 'ir.actions.act_window_close'}
