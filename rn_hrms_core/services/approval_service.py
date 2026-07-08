# -*- coding: utf-8 -*-
"""Generic approval workflow service."""

import logging

from odoo import models

_logger = logging.getLogger(__name__)


class RnHrmsApprovalService(models.AbstractModel):
    """Submit, approve, and reject HRMS approval requests."""

    _name = 'rn.hrms.approval.service'
    _description = 'HRMS Approval Service'

    def submit(self, approvals):
        for approval in approvals:
            if not approval.manager_id and approval.employee_id.parent_id:
                approval.manager_id = approval.employee_id.parent_id.id
            approval.state = 'pending'
            approval.message_post(body='Approval submitted.')
            self.env['rn.hrms.notification.service'].notify_approval_submitted(approval)
        _logger.info('Submitted %s approvals', len(approvals))
        return True

    def approve(self, approvals):
        approvals.write({'state': 'approved'})
        for approval in approvals:
            approval.message_post(body='Approval approved.')
            self.env['rn.hrms.notification.service'].notify_approval_decision(approval, approved=True)
        return True

    def reject(self, approvals):
        approvals.write({'state': 'rejected'})
        for approval in approvals:
            approval.message_post(body='Approval rejected.')
            self.env['rn.hrms.notification.service'].notify_approval_decision(approval, approved=False)
        return True
