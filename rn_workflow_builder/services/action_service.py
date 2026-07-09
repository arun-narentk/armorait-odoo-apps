# -*- coding: utf-8 -*-
"""Execute workflow action nodes."""

import json
import logging

import requests

from odoo import _, models
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class RnWorkflowActionService(models.AbstractModel):
    """Run create, update, email, webhook, and approval actions."""

    _name = 'rn.workflow.action.service'
    _description = 'Workflow Action Service'

    def execute(self, node, context):
        action = node.action_type
        if action == 'send_email':
            return self._action_send_email(node, context)
        if action == 'send_notification':
            return self._action_send_notification(node, context)
        if action == 'call_webhook':
            return self._action_call_webhook(node, context)
        if action == 'create_record':
            return self._action_create_record(node, context)
        if action == 'update_record':
            return self._action_update_record(node, context)
        if action == 'start_approval':
            return _('Approval hook queued (integrate rn_approval_engine).')
        if action == 'ai_summary':
            return self._action_ai_summary(node, context)
        if action == 'python_code':
            settings = self.env.company._get_workflow_settings()
            if not settings.allow_python_actions:
                raise UserError(_('Python actions are disabled in workflow settings.'))
            return _('Python action skipped in Phase 1 sandbox.')
        return _('No action executed.')

    def _parse_config(self, node):
        if not node.config_json:
            return {}
        try:
            return json.loads(node.config_json)
        except json.JSONDecodeError:
            return {}

    def _action_send_email(self, node, context):
        config = self._parse_config(node)
        partner_ids = config.get('partner_ids', [])
        subject = config.get('subject', 'Workflow notification')
        body = config.get('body', 'Automated workflow notification.')
        self.env['mail.mail'].sudo().create({
            'subject': subject,
            'body_html': body,
            'recipient_ids': [(6, 0, partner_ids)],
        }).send()
        return _('Email sent.')

    def _action_send_notification(self, node, context):
        config = self._parse_config(node)
        user_ids = config.get('user_ids', [self.env.user.id])
        self.env['bus.bus']._sendone(
            self.env['res.users'].browse(user_ids),
            'rn_workflow_notification',
            {'message': config.get('message', 'Workflow step completed.')},
        )
        return _('Notification sent.')

    def _action_call_webhook(self, node, context):
        config = self._parse_config(node)
        url = config.get('url') or node.compare_value
        if not url:
            raise UserError(_('Webhook URL is required.'))
        settings = self.env.company._get_workflow_settings()
        if not settings.allow_external_webhooks:
            raise UserError(_('External webhooks are disabled.'))
        payload = {
            'model': context.get('record_model'),
            'res_id': context.get('record_id'),
            'payload': context.get('payload', {}),
        }
        response = requests.post(url, json=payload, timeout=15)
        response.raise_for_status()
        return _('Webhook called: HTTP %s') % response.status_code

    def _action_create_record(self, node, context):
        if not node.target_model_name:
            raise UserError(_('Target model is required for create action.'))
        config = self._parse_config(node)
        vals = config.get('values', {})
        if not vals:
            vals = {'name': config.get('name', 'Workflow created record')}
        record = self.env[node.target_model_name].sudo().create(vals)
        return _('Created %s (#%s)') % (node.target_model_name, record.id)

    def _action_update_record(self, node, context):
        model = context.get('record_model')
        res_id = context.get('record_id')
        if not model or not res_id:
            raise UserError(_('No trigger record to update.'))
        config = self._parse_config(node)
        vals = config.get('values', {})
        if vals:
            self.env[model].browse(res_id).sudo().write(vals)
        return _('Updated record %s') % res_id

    def _action_ai_summary(self, node, context):
        summary = self.env['rn.workflow.ai.service'].summarize_context(context)
        config = self._parse_config(node)
        if config.get('post_to_chatter') and context.get('record_model') and context.get('record_id'):
            record = self.env[context['record_model']].browse(context['record_id'])
            if hasattr(record, 'message_post'):
                record.message_post(body=summary, subtype_xmlid='mail.mt_note')
        return summary
