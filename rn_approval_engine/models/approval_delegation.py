# -*- coding: utf-8 -*-
"""Delegate approvals when approvers are away."""

from odoo import api, fields, models


class RnApprovalDelegation(models.Model):
    """Temporary approval delegation between users."""

    _name = 'rn.approval.delegation'
    _description = 'Approval Delegation'
    _order = 'date_start desc'

    name = fields.Char(compute='_compute_name', store=True)
    user_id = fields.Many2one('res.users', required=True, index=True)
    delegate_user_id = fields.Many2one('res.users', required=True, index=True)
    date_start = fields.Date(required=True)
    date_end = fields.Date(required=True)
    active = fields.Boolean(default=True)
    company_id = fields.Many2one(
        'res.company',
        required=True,
        default=lambda self: self.env.company,
        index=True,
    )

    @api.depends('user_id', 'delegate_user_id')
    def _compute_name(self):
        for rec in self:
            rec.name = f'{rec.user_id.name or ""} -> {rec.delegate_user_id.name or ""}'
