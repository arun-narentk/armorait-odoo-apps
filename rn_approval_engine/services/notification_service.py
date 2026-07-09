# -*- coding: utf-8 -*-
"""Email notifications for approval events."""

import logging

from odoo import models

_logger = logging.getLogger(__name__)


class RnApprovalNotificationService(models.AbstractModel):
    """Send mail notifications to approvers and requesters."""

    _name = 'rn.approval.notification.service'
    _description = 'Approval Notification Service'

    def notify_pending_approvers(self, request):
        settings = self._get_settings(request.company_id.id)
        if not settings.enable_email_notify:
            return
        template = self.env.ref(
            'rn_approval_engine.mail_template_approval_pending',
            raise_if_not_found=False,
        )
        if not template:
            return
        pending_users = request.line_ids.filtered(
            lambda l: l.is_active_stage and l.state == 'pending'
        ).mapped('user_id')
        for user in pending_users:
            template.with_context(approver_name=user.name).send_mail(
                request.id,
                force_send=False,
                email_values={'email_to': user.email},
            )

    def notify_requester(self, request, event):
        settings = self._get_settings(request.company_id.id)
        if not settings.enable_email_notify or not request.requester_id.email:
            return
        subject_map = {
            'approved': 'Your approval request was approved',
            'rejected': 'Your approval request was rejected',
            'changes': 'Changes requested on your approval',
        }
        request.message_post(
            body=subject_map.get(event, 'Approval update'),
            partner_ids=request.requester_id.partner_id.ids,
        )

    def _get_settings(self, company_id):
        settings = self.env['rn.approval.settings'].search(
            [('company_id', '=', company_id)], limit=1,
        )
        if not settings:
            settings = self.env['rn.approval.settings'].create({
                'company_id': company_id,
            })
        return settings
