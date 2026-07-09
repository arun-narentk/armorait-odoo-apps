# -*- coding: utf-8 -*-
"""Submit document for approval."""

from odoo import api, fields, models
from odoo.exceptions import UserError


class RnApprovalSubmitWizard(models.TransientModel):
    _name = 'rn.approval.submit.wizard'
    _description = 'Submit for Approval'

    res_model = fields.Char(required=True)
    res_id = fields.Integer(required=True)
    amount = fields.Monetary(currency_field='currency_id')
    currency_id = fields.Many2one(
        'res.currency',
        default=lambda self: self.env.company.currency_id,
    )
    workflow_id = fields.Many2one('rn.approval.workflow')
    note = fields.Text(string='Submission Note')

    @api.onchange('res_model', 'res_id', 'amount')
    def _onchange_pick_workflow(self):
        if self.res_model:
            workflow = self.env['rn.approval.rule.service'].find_workflow(
                self.res_model,
                amount=self.amount or 0.0,
                company_id=self.env.company.id,
            )
            self.workflow_id = workflow

    def action_submit(self):
        self.ensure_one()
        if not self.workflow_id:
            raise UserError('No approval workflow matched this document.')
        doc = self.env[self.res_model].browse(self.res_id)
        if not doc.exists():
            raise UserError('Document not found.')

        if doc.approval_request_id and doc.approval_request_id.state in ('pending', 'approved'):
            raise UserError('This document already has an active approval request.')

        request = self.env['rn.approval.request'].create({
            'workflow_id': self.workflow_id.id,
            'res_model': self.res_model,
            'res_id': self.res_id,
            'amount': self.amount,
            'currency_id': self.currency_id.id,
            'company_id': self.env.company.id,
        })
        doc.approval_request_id = request.id
        if self.note:
            request.message_post(body=self.note)
        self.env['rn.approval.engine.service'].submit_request(request)
        return {
            'type': 'ir.actions.act_window',
            'name': 'Approval Request',
            'res_model': 'rn.approval.request',
            'view_mode': 'form',
            'res_id': request.id,
        }
