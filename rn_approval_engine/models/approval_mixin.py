# -*- coding: utf-8 -*-
"""Mixin for documents that support approval."""

from odoo import fields, models


class RnApprovalMixin(models.AbstractModel):
    """Add approval request linkage to business documents."""

    _name = 'rn.approval.mixin'
    _description = 'Approval Mixin'

    approval_request_id = fields.Many2one('rn.approval.request', copy=False)
    approval_state = fields.Selection(
        related='approval_request_id.state',
        string='Approval Status',
        store=True,
    )
    requires_approval = fields.Boolean(default=False)

    def action_submit_for_approval(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Submit for Approval',
            'res_model': 'rn.approval.submit.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_res_model': self._name,
                'default_res_id': self.id,
                'default_amount': getattr(self, 'amount_total', 0.0) or 0.0,
            },
        }

    def action_open_approval_request(self):
        self.ensure_one()
        if not self.approval_request_id:
            return False
        return {
            'type': 'ir.actions.act_window',
            'name': 'Approval Request',
            'res_model': 'rn.approval.request',
            'view_mode': 'form',
            'res_id': self.approval_request_id.id,
        }
