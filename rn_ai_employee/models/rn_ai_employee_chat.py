# -*- coding: utf-8 -*-
"""Chat session model."""

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class AiEmployeeChat(models.Model):
    _name = 'rn.ai.employee.chat'
    _description = 'AI Copilot Chat Session'
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
    agent_id = fields.Many2one(
        'rn.ai.employee.agent',
        string='Domain Agent',
        index=True,
        ondelete='set null',
        help='When set, only skills assigned to this domain agent are available.',
    )
    active = fields.Boolean(default=True)
    message_ids = fields.One2many(
        'rn.ai.employee.message',
        'chat_id',
        string='Messages',
    )
    message_count = fields.Integer(compute='_compute_message_count')
    draft_message = fields.Text(string='Message', store=False)
    suggested_question_id = fields.Many2one('rn.ai.employee.suggestion', string='Suggested Question')
    last_message_preview = fields.Char(compute='_compute_last_message_preview')
    memory_context = fields.Text(
        string='Session Memory',
        help='JSON context from recent tool results for follow-up questions.',
        groups='rn_ai_employee.group_rn_ai_employee_manager',
    )

    @api.depends('message_ids')
    def _compute_message_count(self):
        grouped = self.env['rn.ai.employee.message'].read_group(
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
            'rn_ai_employee.group_rn_ai_employee_manager'
        ):
            raise UserError(_('You can only send messages in your own conversations.'))

        message = (self.draft_message or '').strip()
        if not message:
            raise UserError(_('Please type a message before sending.'))

        try:
            self.env['rn.ai.employee.service'].process_chat_message(self, message)
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
                    'res_model': 'rn.ai.employee.chat',
                    'res_id': self.id,
                    'view_mode': 'form',
                    'target': 'current',
                },
            },
        }

    @api.model
    def action_start_new_chat(self):
        """Create a chat and open its form view."""
        agent_id = self.env.context.get('default_agent_id')
        chat = self.create({
            'name': _('Business question'),
            'agent_id': agent_id,
        })
        return {
            'type': 'ir.actions.act_window',
            'name': _('AI Copilot'),
            'res_model': 'rn.ai.employee.chat',
            'res_id': chat.id,
            'view_mode': 'form',
            'target': 'current',
        }

    def action_ask_selected_suggestion(self):
        """Send the selected suggested question."""
        self.ensure_one()
        if not self.suggested_question_id:
            raise UserError(_('Pick a suggested question first.'))
        self.env['rn.ai.employee.service'].process_chat_message(
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
        self.env['rn.ai.employee.service'].process_chat_message(self, question)
        return self._reload_form()

    def _reload_form(self):
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'rn.ai.employee.chat',
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'current',
        }

    @api.model
    def _widget_enabled(self) -> bool:
        if not self.env.user.has_group('rn_ai_employee.group_rn_ai_employee_user'):
            raise UserError(_('You do not have access to AI Copilot.'))
        enabled = self.env['ir.config_parameter'].sudo().get_param('rn_ai_employee.enabled', 'False') == 'True'
        if not enabled:
            raise UserError(_('AI Copilot is disabled. Enable it under AI Copilot > Settings.'))
        return True

    @api.model
    def _get_or_create_widget_chat(self, agent=None):
        self._widget_enabled()
        agent = agent or self.env['rn.ai.employee.agent'].get_default_agent()
        domain = [
            ('user_id', '=', self.env.user.id),
            ('name', '=', 'Systray Chat'),
            ('active', '=', True),
        ]
        if agent:
            domain.append(('agent_id', '=', agent.id))
        chat = self.search(domain, limit=1)
        if not chat:
            chat = self.create({
                'name': 'Systray Chat',
                'agent_id': agent.id if agent else False,
            })
        else:
            self.env['rn.ai.employee.service'].ensure_system_message(chat)
        return chat

    @api.model
    def widget_bootstrap(self, agent_id=None):
        """Return chat state for the OWL systray widget."""
        Agent = self.env['rn.ai.employee.agent']
        agents = Agent.search([('active', '=', True)], order='sequence, id')
        agent = Agent.browse(agent_id) if agent_id else Agent.get_default_agent()
        if agent_id and (not agent or not agent.active):
            raise UserError(_('This domain agent is not available.'))
        chat = self._get_or_create_widget_chat(agent)
        if agent and chat.agent_id != agent:
            chat.agent_id = agent.id
            chat.message_ids.filtered(lambda msg: msg.role == 'system').unlink()
            self.env['rn.ai.employee.service'].ensure_system_message(chat)

        from ..services.agent_service import get_agent_service

        agent_service = get_agent_service(self.env)
        active_agent = agent_service.get_chat_agent(chat)
        suggestions = agent_service.get_suggestions(active_agent, limit=6)
        return {
            'chat_id': chat.id,
            'agent_id': chat.agent_id.id if chat.agent_id else False,
            'agents': Agent.serialize_for_widget(agents),
            'messages': self._serialize_widget_messages(chat),
            'suggestions': [{
                'id': suggestion.id,
                'label': suggestion.name,
                'question': suggestion.question,
            } for suggestion in suggestions],
        }

    @api.model
    def widget_set_agent(self, chat_id: int, agent_id: int):
        """Switch the systray conversation to another domain agent."""
        self._widget_enabled()
        chat = self.browse(chat_id)
        if chat.user_id != self.env.user:
            raise UserError(_('You can only use your own AI Copilot conversations.'))
        agent = self.env['rn.ai.employee.agent'].browse(agent_id)
        if not agent or not agent.active:
            raise UserError(_('This domain agent is not available.'))
        chat.agent_id = agent.id
        chat.message_ids.filtered(lambda msg: msg.role == 'system').unlink()
        self.env['rn.ai.employee.service'].ensure_system_message(chat)
        return self.widget_bootstrap(agent_id=agent.id)

    @api.model
    def widget_send_message(self, chat_id: int, message: str):
        """Send a message from the systray widget and return refreshed state."""
        self._widget_enabled()
        chat = self.browse(chat_id)
        if chat.user_id != self.env.user:
            raise UserError(_('You can only use your own AI Copilot conversations.'))
        self.env['rn.ai.employee.service'].process_chat_message(chat, message)
        return {
            'chat_id': chat.id,
            'messages': self._serialize_widget_messages(chat),
        }

    @api.model
    def widget_run_action(self, action_id: int):
        """Execute a message action card from the widget."""
        self._widget_enabled()
        action = self.env['rn.ai.employee.message.action'].browse(action_id)
        action.message_id.chat_id._check_widget_access()
        if action.action_type in ('confirm_write', 'cancel_write'):
            client_action = action.action_run()
            chat = action.message_id.chat_id
            if isinstance(client_action, dict) and client_action.get('type') == 'ir.actions.act_window':
                return {
                    'chat_id': chat.id,
                    'messages': self._serialize_widget_messages(chat),
                }
        return action.action_run()

    def _check_widget_access(self):
        self.ensure_one()
        if self.user_id != self.env.user and not self.env.user.has_group(
            'rn_ai_employee.group_rn_ai_employee_manager'
        ):
            raise UserError(_('You can only open your own AI Copilot conversations.'))

    @api.model
    def _serialize_widget_messages(self, chat):
        visible = chat.message_ids.filtered(
            lambda msg: msg.role in ('user', 'assistant', 'system')
        ).sorted('create_date')
        payload = []
        for message in visible:
            payload.append({
                'id': message.id,
                'role': message.role,
                'headline': message.headline or '',
                'content': message.content or '',
                'actions': [{
                    'id': action.id,
                    'label': action.label,
                    'type': action.action_type,
                } for action in message.action_ids],
            })
        return payload

    @api.model_create_multi
    def create(self, vals_list):
        chats = super().create(vals_list)
        service = self.env['rn.ai.employee.service']
        for chat in chats:
            service.ensure_system_message(chat)
        return chats
