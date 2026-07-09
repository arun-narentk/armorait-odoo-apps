# -*- coding: utf-8 -*-
"""Core approval engine: submit, advance stages, approve/reject."""

import logging
from datetime import timedelta

from odoo import fields, models
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class RnApprovalEngineService(models.AbstractModel):
    """Orchestrate approval request lifecycle."""

    _name = 'rn.approval.engine.service'
    _description = 'Approval Engine Service'

    def submit_request(self, request):
        request.ensure_one()
        workflow = request.workflow_id
        if not workflow.stage_ids:
            raise UserError('Workflow has no stages configured.')

        request.line_ids.unlink()
        risk_html = self.env['rn.approval.risk.service'].build_risk_summary(request)
        request.write({
            'state': 'pending',
            'risk_summary': risk_html,
        })
        self._log_history(request, 'submit', comment='Approval submitted')
        self._activate_next_stage(request)
        self.env['rn.approval.notification.service'].notify_pending_approvers(request)
        return request

    def process_line_action(self, line, action):
        line.ensure_one()
        if line.user_id != self.env.user and not self.env.user.has_group(
            'rn_approval_engine.group_rn_approval_manager'
        ):
            raise UserError('You are not the assigned approver for this line.')

        line.write({
            'state': 'approved' if action == 'approve' else 'rejected',
            'action_type': action,
        })
        self._log_history(
            line.request_id,
            action if action in ('approve', 'reject', 'changes') else 'approve',
            stage_name=line.stage_id.name,
            comment=line.comment,
        )

        request = line.request_id
        if action == 'reject':
            request.write({'state': 'rejected'})
            self.env['rn.approval.notification.service'].notify_requester(request, 'rejected')
            return request

        if action == 'changes':
            request.write({'state': 'draft'})
            self.env['rn.approval.notification.service'].notify_requester(request, 'changes')
            return request

        if self._stage_complete(request, line.stage_id):
            if self._has_more_stages(request, line.stage_id):
                self._activate_next_stage(request, after_stage=line.stage_id)
            else:
                request.write({'state': 'approved'})
                self._on_fully_approved(request)
                self.env['rn.approval.notification.service'].notify_requester(request, 'approved')
        return request

    def _activate_next_stage(self, request, after_stage=None):
        stages = request.workflow_id.stage_ids.sorted('sequence')
        next_stage = False
        if after_stage:
            found = False
            for stage in stages:
                if found:
                    next_stage = stage
                    break
                if stage.id == after_stage.id:
                    found = True
        else:
            next_stage = stages[:1]

        if not next_stage:
            return

        if self._should_skip_stage(request, next_stage):
            self._log_history(request, 'skip', stage_name=next_stage.name)
            return self._activate_next_stage(request, after_stage=next_stage)

        request.line_ids.write({'is_active_stage': False})
        approvers = self._resolve_approvers(request, next_stage)
        if not approvers:
            raise UserError(f'Stage "{next_stage.name}" has no approvers configured.')

        deadline = fields.Datetime.now() + timedelta(hours=next_stage.sla_hours or 24)
        Line = self.env['rn.approval.request.line']
        for user in approvers:
            delegate = self._resolve_delegate(user, request.company_id.id)
            Line.create({
                'request_id': request.id,
                'stage_id': next_stage.id,
                'sequence': next_stage.sequence,
                'user_id': delegate.id,
                'deadline': deadline,
                'is_active_stage': True,
                'delegated_from_id': delegate.id != user.id and user.id or False,
            })

        request.write({
            'current_stage_id': next_stage.id,
            'sla_deadline': deadline,
        })
        self.env['rn.approval.notification.service'].notify_pending_approvers(request)

    def _resolve_approvers(self, request, stage):
        Users = self.env['res.users']
        if stage.approver_type == 'user' and stage.user_id:
            return stage.user_id
        if stage.approver_type == 'group' and stage.group_id:
            return stage.group_id.user_ids.filtered(lambda u: u.active)
        if stage.approver_type == 'manager':
            employee = self.env['hr.employee'].search([
                ('user_id', '=', request.requester_id.id),
                ('company_id', '=', request.company_id.id),
            ], limit=1)
            if employee.parent_id and employee.parent_id.user_id:
                return employee.parent_id.user_id
            return Users
        return Users

    def _resolve_delegate(self, user, company_id):
        today = fields.Date.context_today(self)
        delegation = self.env['rn.approval.delegation'].search([
            ('user_id', '=', user.id),
            ('company_id', '=', company_id),
            ('active', '=', True),
            ('date_start', '<=', today),
            ('date_end', '>=', today),
        ], limit=1)
        return delegation.delegate_user_id if delegation else user

    def _should_skip_stage(self, request, stage):
        amount = request.amount or 0.0
        if stage.skip_if_amount_below and amount < stage.skip_if_amount_below:
            return True
        if stage.require_if_new_vendor and request.res_model == 'purchase.order':
            po = self.env['purchase.order'].browse(request.res_id)
            if po.exists() and po.partner_id:
                prior = self.env['purchase.order'].search_count([
                    ('partner_id', '=', po.partner_id.id),
                    ('company_id', '=', request.company_id.id),
                    ('id', '!=', po.id),
                    ('state', 'in', ('purchase', 'done')),
                ])
                return prior > 0
        return False

    def _stage_complete(self, request, stage):
        lines = request.line_ids.filtered(lambda l: l.stage_id == stage)
        if not lines:
            return False
        if stage.stage_mode == 'parallel':
            approved = len(lines.filtered(lambda l: l.state == 'approved'))
            return approved >= (stage.required_approvals or len(lines))
        return all(line.state == 'approved' for line in lines)

    def _has_more_stages(self, request, current_stage):
        stages = request.workflow_id.stage_ids.sorted('sequence')
        return any(s.sequence > current_stage.sequence for s in stages)

    def _on_fully_approved(self, request):
        doc = self.env[request.res_model].browse(request.res_id)
        if doc.exists() and hasattr(doc, 'message_post'):
            doc.message_post(body=f'Approval {request.reference} completed.')

    def _log_history(self, request, action, stage_name=None, comment=None):
        self.env['rn.approval.history'].create({
            'request_id': request.id,
            'user_id': self.env.user.id,
            'action': action,
            'stage_name': stage_name,
            'comment': comment,
        })
