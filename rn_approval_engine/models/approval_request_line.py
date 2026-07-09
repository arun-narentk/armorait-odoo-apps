# -*- coding: utf-8 -*-
"""Per-approver action lines."""

from odoo import fields, models
from odoo.exceptions import UserError

LINE_STATES = [
    ('pending', 'Pending'),
    ('approved', 'Approved'),
    ('rejected', 'Rejected'),
    ('skipped', 'Skipped'),
    ('delegated', 'Delegated'),
]


class RnApprovalRequestLine(models.Model):
    """Approver line for a request stage."""

    _name = 'rn.approval.request.line'
    _description = 'Approval Request Line'
    _order = 'sequence, id'

    request_id = fields.Many2one(
        'rn.approval.request',
        required=True,
        ondelete='cascade',
        index=True,
    )
    stage_id = fields.Many2one('rn.approval.workflow.stage', required=True)
    sequence = fields.Integer(default=10)
    user_id = fields.Many2one('res.users', required=True, index=True)
    state = fields.Selection(selection=LINE_STATES, default='pending', index=True)
    action_type = fields.Selection(
        selection=[
            ('approve', 'Approved'),
            ('reject', 'Rejected'),
            ('changes', 'Changes Requested'),
        ],
    )
    comment = fields.Text()
    deadline = fields.Datetime()
    delegated_from_id = fields.Many2one('res.users', string='Delegated From')
    is_active_stage = fields.Boolean(default=False)
    company_id = fields.Many2one(related='request_id.company_id', store=True)

    def action_approve(self):
        for line in self:
            if line.state != 'pending':
                raise UserError('This approval line is no longer pending.')
            self.env['rn.approval.engine.service'].process_line_action(line, 'approve')
        return True

    def action_reject(self):
        for line in self:
            if line.state != 'pending':
                raise UserError('This approval line is no longer pending.')
            self.env['rn.approval.engine.service'].process_line_action(line, 'reject')
        return True

    def action_request_changes(self):
        for line in self:
            if line.state != 'pending':
                raise UserError('This approval line is no longer pending.')
            self.env['rn.approval.engine.service'].process_line_action(line, 'changes')
        return True
