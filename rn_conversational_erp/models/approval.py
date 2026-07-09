# -*- coding: utf-8 -*-
"""Approval center for conversational workflows."""

from odoo import fields, models


class RnConversationalErpApproval(models.Model):
    _name = 'rn.conversational.erp.approval'
    _description = 'Conversational ERP Approval'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'create_date desc'

    name = fields.Char(required=True, copy=False, default='New', tracking=True)
    company_id = fields.Many2one('res.company', required=True, default=lambda self: self.env.company)
    conversation_id = fields.Many2one('rn.conversational.erp.conversation', ondelete='set null')
    request_model = fields.Char()
    request_res_id = fields.Integer()
    requester_id = fields.Many2one('res.users', default=lambda self: self.env.user)
    approver_id = fields.Many2one('res.users', required=True)
    amount = fields.Monetary(currency_field='currency_id')
    currency_id = fields.Many2one('res.currency', default=lambda self: self.env.company.currency_id)
    state = fields.Selection(
        [('pending', 'Pending'), ('approved', 'Approved'), ('rejected', 'Rejected')],
        default='pending',
        tracking=True,
    )
    summary = fields.Text(required=True)

    def action_approve(self):
        self.write({'state': 'approved'})
        return True

    def action_reject(self):
        self.write({'state': 'rejected'})
        return True
