# -*- coding: utf-8 -*-
"""Action cards attached to assistant answers."""

from __future__ import annotations

import json
import logging

from odoo import _, api, fields, models
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class AiEmployeeMessageAction(models.Model):
    _name = 'rn.ai.employee.message.action'
    _description = 'AI Employee Message Action'
    _order = 'sequence, id'

    message_id = fields.Many2one(
        'rn.ai.employee.message',
        required=True,
        ondelete='cascade',
        index=True,
    )
    label = fields.Char(required=True)
    action_type = fields.Selection(
        selection=[
            ('open_list', 'Open List'),
            ('create_activity', 'Create Activity'),
            ('open_form', 'Open Record'),
            ('export_list', 'Export'),
            ('confirm_write', 'Confirm Write'),
            ('cancel_write', 'Cancel Write'),
            ('phase2', 'Coming Soon'),
        ],
        required=True,
        default='open_list',
    )
    res_model = fields.Char()
    domain = fields.Text(default='[]')
    res_ids = fields.Text(default='[]')
    sequence = fields.Integer(default=10)

    def action_run(self):
        """Execute the selected action card."""
        self.ensure_one()
        if self.action_type == 'open_list':
            return self._action_open_list()
        if self.action_type == 'open_form':
            return self._action_open_form()
        if self.action_type == 'create_activity':
            return self._action_create_activity()
        if self.action_type == 'export_list':
            return self._action_open_list()
        if self.action_type == 'confirm_write':
            return self._action_confirm_write()
        if self.action_type == 'cancel_write':
            return self._action_cancel_write()
        raise UserError(_('This action will be available in a future release.'))

    def _action_open_list(self):
        self.ensure_one()
        domain = json.loads(self.domain or '[]')
        res_ids = json.loads(self.res_ids or '[]')
        action = {
            'type': 'ir.actions.act_window',
            'name': self.label,
            'res_model': self.res_model,
            'view_mode': 'list,form',
            'domain': domain,
            'target': 'current',
        }
        if res_ids:
            action['domain'] = [('id', 'in', res_ids)]
        return action

    def _action_open_form(self):
        self.ensure_one()
        res_ids = json.loads(self.res_ids or '[]')
        if not res_ids or not self.res_model:
            raise UserError(_('No record available to open.'))
        return {
            'type': 'ir.actions.act_window',
            'name': self.label,
            'res_model': self.res_model,
            'res_id': res_ids[0],
            'view_mode': 'form',
            'target': 'current',
        }

    def _action_create_activity(self):
        self.ensure_one()
        res_ids = json.loads(self.res_ids or '[]')
        if not res_ids or not self.res_model:
            raise UserError(_('No records available for follow-up activity.'))
        return {
            'type': 'ir.actions.act_window',
            'name': _('Schedule Activity'),
            'res_model': 'mail.activity.schedule',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_res_model': self.res_model,
                'default_res_ids': res_ids[:50],
            },
        }

    def _action_confirm_write(self):
        self.ensure_one()
        pending = self._get_pending_action()
        pending.action_confirm()
        return pending.chat_id._reload_form()

    def _action_cancel_write(self):
        self.ensure_one()
        pending = self._get_pending_action()
        pending.action_cancel()
        return pending.chat_id._reload_form()

    def _get_pending_action(self):
        self.ensure_one()
        res_ids = json.loads(self.res_ids or '[]')
        if not res_ids:
            raise UserError(_('No pending action is linked to this card.'))
        pending = self.env['rn.ai.employee.pending.action'].browse(res_ids[0])
        if not pending.exists():
            raise UserError(_('The pending action is no longer available.'))
        return pending

    @api.model
    def create_from_tool_result(self, message, result: dict) -> None:
        """Persist action cards from structured tool output."""
        for index, action in enumerate(result.get('suggested_actions') or []):
            self.create({
                'message_id': message.id,
                'label': action.get('label'),
                'action_type': action.get('action_type', 'open_list'),
                'res_model': action.get('res_model'),
                'domain': json.dumps(action.get('domain') or [], default=str),
                'res_ids': json.dumps(action.get('res_ids') or [], default=str),
                'sequence': (index + 1) * 10,
            })
