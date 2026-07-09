# -*- coding: utf-8 -*-

from odoo import api, fields, models


class RnJewelleryJobWork(models.Model):
    _name = 'rn.jewellery.job.work'
    _description = 'Job Work Issue / Receive'
    _inherit = ['mail.thread']
    _order = 'work_date desc'

    name = fields.Char(readonly=True, copy=False, default='New')
    job_card_id = fields.Many2one('rn.jewellery.job.card', required=True, ondelete='cascade', index=True)
    karigar_id = fields.Many2one('rn.jewellery.karigar', required=True, index=True)
    work_date = fields.Date(required=True, default=fields.Date.context_today)
    issue_weight = fields.Float(string='Issue Weight (g)', digits=(16, 3))
    receive_weight = fields.Float(string='Receive Weight (g)', digits=(16, 3))
    wastage_weight = fields.Float(compute='_compute_wastage', store=True, digits=(16, 3))
    state = fields.Selection(
        [
            ('issued', 'Gold Issued'),
            ('in_production', 'In Production'),
            ('received', 'Received'),
            ('qc_pass', 'QC Passed'),
            ('qc_fail', 'QC Failed'),
        ],
        default='issued',
        tracking=True,
    )
    note = fields.Text()
    company_id = fields.Many2one(related='job_card_id.company_id', store=True, index=True)

    @api.depends('issue_weight', 'receive_weight')
    def _compute_wastage(self):
        for work in self:
            work.wastage_weight = max((work.issue_weight or 0.0) - (work.receive_weight or 0.0), 0.0)

    @api.model_create_multi
    def create(self, vals_list):
        seq = self.env['ir.sequence']
        for vals in vals_list:
            if vals.get('name', 'New') == 'New':
                vals['name'] = seq.next_by_code('rn.jewellery.job.work') or 'JW'
        return super().create(vals_list)
