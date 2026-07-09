# -*- coding: utf-8 -*-

from odoo import api, fields, models


class RnConstructionRunningBill(models.Model):
    _name = 'rn.construction.running.bill'
    _description = 'Running Bill / RA Bill'
    _inherit = ['mail.thread']
    _order = 'bill_date desc'

    name = fields.Char(readonly=True, copy=False, default='New')
    construction_project_id = fields.Many2one(
        'rn.construction.project',
        required=True,
        ondelete='cascade',
        index=True,
    )
    bill_date = fields.Date(required=True, default=fields.Date.context_today)
    milestone_id = fields.Many2one('rn.construction.milestone')
    work_done_amount = fields.Float(required=True)
    retention_pct = fields.Float(string='Retention %', default=5.0)
    retention_amount = fields.Float(compute='_compute_amounts', store=True)
    net_payable = fields.Float(compute='_compute_amounts', store=True)
    state = fields.Selection(
        [('draft', 'Draft'), ('submitted', 'Submitted'), ('approved', 'Approved'), ('invoiced', 'Invoiced')],
        default='draft',
        tracking=True,
    )
    invoice_id = fields.Many2one('account.move', copy=False)
    company_id = fields.Many2one(related='construction_project_id.company_id', store=True, index=True)

    @api.depends('work_done_amount', 'retention_pct')
    def _compute_amounts(self):
        for bill in self:
            retention = (bill.work_done_amount or 0.0) * (bill.retention_pct or 0.0) / 100.0
            bill.retention_amount = retention
            bill.net_payable = (bill.work_done_amount or 0.0) - retention

    @api.model_create_multi
    def create(self, vals_list):
        seq = self.env['ir.sequence']
        for vals in vals_list:
            if vals.get('name', 'New') == 'New':
                vals['name'] = seq.next_by_code('rn.construction.running.bill') or 'RB'
        return super().create(vals_list)
