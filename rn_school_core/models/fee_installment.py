# -*- coding: utf-8 -*-

from odoo import api, fields, models


class RnSchoolFeeInstallment(models.Model):
    _name = 'rn.school.fee.installment'
    _description = 'Student Fee Installment'
    _order = 'due_date'

    student_id = fields.Many2one('rn.school.student', required=True, index=True)
    fee_structure_id = fields.Many2one('rn.school.fee.structure')
    name = fields.Char(required=True)
    due_date = fields.Date(required=True, index=True)
    amount = fields.Float(required=True)
    discount = fields.Float()
    scholarship = fields.Float()
    net_amount = fields.Float(compute='_compute_net', store=True)
    state = fields.Selection(
        [('draft', 'Draft'), ('due', 'Due'), ('paid', 'Paid'), ('overdue', 'Overdue')],
        default='draft',
    )
    invoice_id = fields.Many2one('account.move', copy=False)
    company_id = fields.Many2one(
        related='student_id.company_id',
        store=True,
        index=True,
    )

    @api.depends('amount', 'discount', 'scholarship')
    def _compute_net(self):
        for rec in self:
            rec.net_amount = max((rec.amount or 0) - (rec.discount or 0) - (rec.scholarship or 0), 0.0)
