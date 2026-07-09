# -*- coding: utf-8 -*-
"""Immutable approval audit trail."""

from odoo import fields, models


class RnApprovalHistory(models.Model):
    """Audit log entry for approval actions."""

    _name = 'rn.approval.history'
    _description = 'Approval History'
    _order = 'create_date desc'

    request_id = fields.Many2one(
        'rn.approval.request',
        required=True,
        ondelete='cascade',
        index=True,
    )
    user_id = fields.Many2one('res.users', required=True)
    action = fields.Selection(
        selection=[
            ('submit', 'Submitted'),
            ('approve', 'Approved'),
            ('reject', 'Rejected'),
            ('changes', 'Changes Requested'),
            ('skip', 'Stage Skipped'),
            ('escalate', 'Escalated'),
            ('cancel', 'Cancelled'),
        ],
        required=True,
    )
    stage_name = fields.Char()
    comment = fields.Text()
    company_id = fields.Many2one(related='request_id.company_id', store=True)
