# -*- coding: utf-8 -*-

from odoo import api, fields, models


class RnDentalLabRequest(models.Model):
    _name = 'rn.dental.lab.request'
    _description = 'Dental Lab Request'
    _inherit = ['mail.thread']
    _order = 'create_date desc'

    name = fields.Char(readonly=True, copy=False, default='New')
    patient_id = fields.Many2one('rn.dental.patient', required=True, index=True)
    dentist_id = fields.Many2one('hr.employee', string='Dentist')
    treatment_plan_id = fields.Many2one('rn.dental.treatment.plan')
    work_type = fields.Selection(
        [
            ('crown', 'Crown'),
            ('bridge', 'Bridge'),
            ('denture', 'Denture'),
            ('veneer', 'Veneer'),
            ('implant_abutment', 'Implant Abutment'),
            ('other', 'Other'),
        ],
        default='crown',
        required=True,
    )
    lab_partner_id = fields.Many2one('res.partner', string='Laboratory')
    request_date = fields.Date(default=fields.Date.context_today, required=True)
    due_date = fields.Date()
    received_date = fields.Date()
    state = fields.Selection(
        [
            ('draft', 'Draft'),
            ('sent', 'Sent to Lab'),
            ('in_progress', 'In Progress'),
            ('ready', 'Ready'),
            ('delivered', 'Delivered to Patient'),
            ('cancelled', 'Cancelled'),
        ],
        default='draft',
        tracking=True,
    )
    note = fields.Text()
    company_id = fields.Many2one(
        'res.company',
        required=True,
        default=lambda self: self.env.company,
        index=True,
    )

    @api.model_create_multi
    def create(self, vals_list):
        seq = self.env['ir.sequence']
        for vals in vals_list:
            if vals.get('name', 'New') == 'New':
                vals['name'] = seq.next_by_code('rn.dental.lab.request') or 'LAB'
        return super().create(vals_list)
