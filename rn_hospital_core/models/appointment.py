# -*- coding: utf-8 -*-

from odoo import api, fields, models


class RnHospitalAppointment(models.Model):
    _name = 'rn.hospital.appointment'
    _description = 'Hospital Appointment'
    _inherit = ['mail.thread']
    _order = 'appointment_datetime desc'

    name = fields.Char(readonly=True, copy=False, default='New')
    patient_id = fields.Many2one('rn.hospital.patient', required=True, index=True)
    doctor_id = fields.Many2one('hr.employee', string='Doctor', index=True, domain=[('is_doctor', '=', True)])
    department_id = fields.Many2one('rn.hospital.department')
    appointment_datetime = fields.Datetime(required=True, index=True)
    appointment_type = fields.Selection(
        [
            ('opd', 'OPD'),
            ('followup', 'Follow-up'),
            ('tele', 'Teleconsultation'),
            ('walkin', 'Walk-in'),
        ],
        default='opd',
    )
    state = fields.Selection(
        [
            ('draft', 'Draft'),
            ('confirmed', 'Confirmed'),
            ('waiting', 'Waiting'),
            ('in_consultation', 'In Consultation'),
            ('done', 'Done'),
            ('cancelled', 'Cancelled'),
            ('no_show', 'No Show'),
        ],
        default='draft',
        required=True,
        tracking=True,
    )
    token_number = fields.Integer(string='Token', copy=False)
    chief_complaint = fields.Text()
    note = fields.Text()
    encounter_id = fields.Many2one('rn.hospital.emr.encounter', copy=False)
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
                vals['name'] = seq.next_by_code('rn.hospital.appointment') or 'APT'
        return super().create(vals_list)

    def action_confirm(self):
        self.write({'state': 'confirmed'})

    def action_check_in(self):
        for appt in self:
            token = self.env['rn.hospital.appointment.service'].assign_token(appt.id)
            appt.write({'state': 'waiting', 'token_number': token})

    def action_start_consultation(self):
        self.write({'state': 'in_consultation'})

    def action_complete(self):
        self.write({'state': 'done'})

    def action_cancel(self):
        self.write({'state': 'cancelled'})
