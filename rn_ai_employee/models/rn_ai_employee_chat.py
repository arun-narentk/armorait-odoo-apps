# -*- coding: utf-8 -*-
"""Chat session model."""

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class AiEmployeeChat(models.Model):
    _name = 'ai.employee.chat'
    _description = 'AI Employee Chat Session'
    _order = 'create_date desc'

    name = fields.Char(
        string='Subject',
        required=True,
        default=lambda self: _('New conversation'),
    )
    user_id = fields.Many2one(
        'res.users',
        string='User',
        required=True,
        default=lambda self: self.env.user,
        index=True,
    )
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        required=True,
        default=lambda self: self.env.company,
        index=True,
    )
    active = fields.Boolean(default=True)
    message_ids = fields.One2many(
        'ai.employee.message',
        'chat_id',
        string='Messages',
    )
    message_count = fields.Integer(compute='_compute_message_count')
    draft_message = fields.Text(string='Message', store=False)
    suggested_question_id = fields.Many2one('ai.employee.suggestion', string='Suggested Question')
    last_message_preview = fields.Char(compute='_compute_last_message_preview')

    @api.depends('message_ids')
    def _compute_message_count(self):
        grouped = self.env['ai.employee.message'].read_group(
            [('chat_id', 'in', self.ids)],
            ['chat_id'],
            ['chat_id'],
        )
        counts = {row['chat_id'][0]: row['chat_id_count'] for row in grouped}
        for chat in self:
            chat.message_count = counts.get(chat.id, 0)

    @api.depends('message_ids', 'message_ids.content', 'message_ids.role')
    def _compute_last_message_preview(self):
        for chat in self:
            last = chat.message_ids.sorted('create_date', reverse=True)[:1]
            preview = (last.content or '')[:120] if last else ''
            chat.last_message_preview = preview

    def action_send_message(self):
        """Send the draft message through the orchestration service."""
        self.ensure_one()
        if self.user_id != self.env.user and not self.env.user.has_group(
            'rn_ai_employee.group_ai_employee_manager'
        ):
            raise UserError(_('You can only send messages in your own conversations.'))

        message = (self.draft_message or '').strip()
        if not message:
            raise UserError(_('Please type a message before sending.'))

        try:
            self.env['ai.employee.service'].process_chat_message(self, message)
        except UserError:
            raise
        except Exception as exc:
            raise UserError(_('Could not send the message: %s') % exc) from exc

        self.draft_message = False
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('AI Copilot'),
                'message': _('Response received.'),
                'type': 'success',
                'sticky': False,
                'next': {
                    'type': 'ir.actions.act_window',
                    'res_model': 'ai.employee.chat',
                    'res_id': self.id,
                    'view_mode': 'form',
                    'target': 'current',
                },
            },
        }

    @api.model
    def action_start_new_chat(self):
        """Create a chat and open its form view."""
        chat = self.create({'name': _('Business question')})
        return {
            'type': 'ir.actions.act_window',
            'name': _('AI Copilot'),
            'res_model': 'ai.employee.chat',
            'res_id': chat.id,
            'view_mode': 'form',
            'target': 'current',
        }

    def action_ask_selected_suggestion(self):
        """Send the selected suggested question."""
        self.ensure_one()
        if not self.suggested_question_id:
            raise UserError(_('Pick a suggested question first.'))
        self.env['ai.employee.service'].process_chat_message(
            self,
            self.suggested_question_id.question,
        )
        self.suggested_question_id = False
        return self._reload_form()

    def action_ask_suggested(self):
        """Send a suggested question from button context."""
        self.ensure_one()
        question = self.env.context.get('suggested_question', '').strip()
        if not question:
            raise UserError(_('No suggested question provided.'))
        self.env['ai.employee.service'].process_chat_message(self, question)
        return self._reload_form()

    def _reload_form(self):
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'ai.employee.chat',
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'current',
        }

    @api.model_create_multi
    def create(self, vals_list):
        chats = super().create(vals_list)
        service = self.env['ai.employee.service']
        for chat in chats:
            service.ensure_system_message(chat)
        return chats
