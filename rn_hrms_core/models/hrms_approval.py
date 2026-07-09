# -*- coding: utf-8 -*-
"""Generic multi-level approval requests used by leave, expense, etc."""

from odoo import api, fields, models


class RnHrmsApproval(models.Model):
    """Central approval document that companion modules can reuse."""

    _name = 'rn.hrms.approval'
    _description = 'HRMS Approval Request'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'create_date desc'

    name = fields.Char(required=True, copy=False, default='New', tracking=True)
    request_type = fields.Selection(
        selection=[
            ('leave', 'Leave'),
            ('attendance', 'Attendance Regularization'),
            ('expense', 'Expense'),
            ('loan', 'Loan'),
            ('travel', 'Travel'),
            ('general', 'General'),
        ],
        required=True,
        default='general',
        index=True,
    )
    employee_id = fields.Many2one('hr.employee', required=True, tracking=True, index=True)
    manager_id = fields.Many2one('hr.employee', string='Approver', tracking=True)
    state = fields.Selection(
        selection=[
            ('draft', 'Draft'),
            ('pending', 'Pending'),
            ('approved', 'Approved'),
            ('rejected', 'Rejected'),
            ('cancel', 'Cancelled'),
        ],
        default='draft',
        tracking=True,
        index=True,
    )
    request_date = fields.Date(default=fields.Date.context_today)
    summary = fields.Char()
    description = fields.Html()
    res_model = fields.Char(index=True)
    res_id = fields.Integer(index=True)
    company_id = fields.Many2one(
        'res.company',
        required=True,
        default=lambda self: self.env.company,
        index=True,
    )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', 'New') == 'New':
                vals['name'] = self.env['ir.sequence'].next_by_code('rn.hrms.approval') or 'New'
        return super().create(vals_list)

    def action_submit(self):
        return self.env['rn.hrms.approval.service'].submit(self)

    def action_approve(self):
        return self.env['rn.hrms.approval.service'].approve(self)

    def action_reject(self):
        return self.env['rn.hrms.approval.service'].reject(self)
