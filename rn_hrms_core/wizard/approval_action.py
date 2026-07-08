# -*- coding: utf-8 -*-
"""Bulk approve / reject wizard."""

from odoo import fields, models


class RnHrmsApprovalActionWizard(models.TransientModel):
    """Apply a decision on selected approvals."""

    _name = 'rn.hrms.approval.action.wizard'
    _description = 'HRMS Approval Action Wizard'

    approval_ids = fields.Many2many('rn.hrms.approval', string='Approvals', required=True)
    action = fields.Selection(
        selection=[('approve', 'Approve'), ('reject', 'Reject')],
        required=True,
        default='approve',
    )
    note = fields.Text()

    def action_apply(self):
        self.ensure_one()
        if self.action == 'approve':
            self.env['rn.hrms.approval.service'].approve(self.approval_ids)
        else:
            self.env['rn.hrms.approval.service'].reject(self.approval_ids)
        if self.note:
            for approval in self.approval_ids:
                approval.message_post(body=self.note)
        return {'type': 'ir.actions.act_window_close'}
