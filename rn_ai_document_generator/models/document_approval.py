# -*- coding: utf-8 -*-
"""Approval steps for generated documents."""

from odoo import fields, models


class RnAiDocumentApproval(models.Model):
    """Single approval / review step."""

    _name = 'rn.ai.document.approval'
    _description = 'AI Document Approval'
    _order = 'sequence, id'

    name = fields.Char(required=True)
    sequence = fields.Integer(default=10)
    document_id = fields.Many2one(
        'rn.ai.document',
        required=True,
        ondelete='cascade',
        index=True,
    )
    role = fields.Selection(
        selection=[
            ('manager', 'Manager'),
            ('legal', 'Legal'),
            ('hr', 'HR'),
            ('finance', 'Finance'),
            ('custom', 'Custom'),
        ],
        default='manager',
        required=True,
    )
    user_id = fields.Many2one('res.users', string='Approver')
    state = fields.Selection(
        selection=[
            ('pending', 'Pending'),
            ('approved', 'Approved'),
            ('rejected', 'Rejected'),
            ('skipped', 'Skipped'),
        ],
        default='pending',
        index=True,
    )
    decision_date = fields.Datetime()
    comment = fields.Text()
    company_id = fields.Many2one(
        related='document_id.company_id',
        store=True,
        index=True,
    )

    def action_approve_step(self):
        self.ensure_one()
        return self.env['rn.ai.document.approval.service'].approve_step(self)

    def action_reject_step(self):
        self.ensure_one()
        return self.env['rn.ai.document.approval.service'].reject_step(self)
