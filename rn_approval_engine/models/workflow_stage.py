# -*- coding: utf-8 -*-
"""Workflow stages: sequential or parallel approver groups."""

from odoo import fields, models


class RnApprovalWorkflowStage(models.Model):
    """Single approval level within a workflow."""

    _name = 'rn.approval.workflow.stage'
    _description = 'Approval Workflow Stage'
    _order = 'sequence, id'

    workflow_id = fields.Many2one(
        'rn.approval.workflow',
        required=True,
        ondelete='cascade',
        index=True,
    )
    name = fields.Char(required=True)
    sequence = fields.Integer(default=10)
    stage_mode = fields.Selection(
        selection=[
            ('sequential', 'Sequential'),
            ('parallel', 'Parallel (all required)'),
        ],
        default='sequential',
        required=True,
    )
    approver_type = fields.Selection(
        selection=[
            ('user', 'Specific User'),
            ('group', 'Security Group'),
            ('manager', 'Requester Manager'),
        ],
        default='group',
        required=True,
    )
    user_id = fields.Many2one('res.users', string='Approver User')
    group_id = fields.Many2one('res.groups', string='Approver Group')
    required_approvals = fields.Integer(
        default=1,
        help='For parallel stages, number of approvals required from the group.',
    )
    sla_hours = fields.Integer(default=24, string='SLA Hours')
    escalate_user_id = fields.Many2one('res.users', string='Escalation User')
    skip_if_amount_below = fields.Monetary(
        string='Skip if Amount Below',
        currency_field='currency_id',
        help='Skip this stage when document amount is below this value.',
    )
    require_if_new_vendor = fields.Boolean(
        string='Require for New Vendor',
        help='Only enforce when vendor has no prior purchase history.',
    )
    currency_id = fields.Many2one(
        'res.currency',
        related='workflow_id.company_id.currency_id',
    )
    company_id = fields.Many2one(related='workflow_id.company_id', store=True)
