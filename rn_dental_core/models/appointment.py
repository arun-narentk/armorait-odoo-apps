# -*- coding: utf-8 -*-

from odoo import api, fields, models


class RnDentalAppointment(models.Model):
    _name = 'rn.dental.appointment'
    _description = 'Dental Appointment'
    _inherit = ['mail.thread']
    _order = 'start_datetime desc'

    name = fields.Char(readonly=True, copy=False, default='New')
    patient_id = fields.Many2one('rn.dental.patient', required=True, index=True)
    dentist_id = fields.Many2one('hr.employee', string='Dentist', required=True, index=True)
    chair_id = fields.Many2one('rn.dental.chair', index=True)
    procedure_id = fields.Many2one('rn.dental.procedure')
    start_datetime = fields.Datetime(required=True, index=True)
    end_datetime = fields.Datetime()
    duration_minutes = fields.Integer(default=30)
    state = fields.Selection(
        [
            ('scheduled', 'Scheduled'),
            ('checked_in', 'Checked In'),
            ('in_chair', 'In Chair'),
            ('completed', 'Completed'),
            ('cancelled', 'Cancelled'),
            ('no_show', 'No Show'),
        ],
        default='scheduled',
        tracking=True,
    )
    note = fields.Text()
    treatment_plan_id = fields.Many2one('rn.dental.treatment.plan')
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
                vals['name'] = seq.next_by_code('rn.dental.appointment') or 'APT'
        return super().create(vals_list)

    def action_check_in(self):
        self.write({'state': 'checked_in'})

    def action_complete(self):
        self.write({'state': 'completed'})
