# -*- coding: utf-8 -*-
"""Core clinic appointments (OPD)."""

from datetime import timedelta

from odoo import api, fields, models


class RnHmsAppointment(models.Model):
    """Patient appointment with doctor / department."""

    _name = 'rn.hms.appointment'
    _description = 'HMS Appointment'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'start_datetime desc, id desc'

    name = fields.Char(required=True, copy=False, default='New', tracking=True)
    state = fields.Selection(
        selection=[
            ('draft', 'Draft'),
            ('confirmed', 'Confirmed'),
            ('waiting', 'Waiting'),
            ('in_consult', 'In Consultation'),
            ('done', 'Done'),
            ('cancel', 'Cancelled'),
            ('no_show', 'No Show'),
        ],
        default='draft',
        tracking=True,
        index=True,
    )
    patient_id = fields.Many2one('rn.hms.patient', required=True, tracking=True, index=True)
    doctor_id = fields.Many2one('rn.hms.doctor', required=True, tracking=True, index=True)
    department_id = fields.Many2one('rn.hms.department', tracking=True)
    appointment_type = fields.Selection(
        selection=[
            ('opd', 'OPD'),
            ('followup', 'Follow-up'),
            ('walkin', 'Walk-in'),
            ('online', 'Online'),
        ],
        default='opd',
        required=True,
    )
    start_datetime = fields.Datetime(required=True, index=True, tracking=True)
    stop_datetime = fields.Datetime(required=True, index=True)
    token_number = fields.Char(copy=False, index=True)
    chief_complaint = fields.Text()
    notes = fields.Html()
    fee = fields.Monetary(currency_field='currency_id')
    currency_id = fields.Many2one(
        'res.currency',
        default=lambda self: self.env.company.currency_id,
    )
    calendar_event_id = fields.Many2one('calendar.event', copy=False)
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
                vals['name'] = self.env['ir.sequence'].next_by_code('rn.hms.appointment') or 'New'
            if not vals.get('stop_datetime') and vals.get('start_datetime') and vals.get('doctor_id'):
                doctor = self.env['rn.hms.doctor'].browse(vals['doctor_id'])
                start = fields.Datetime.to_datetime(vals['start_datetime'])
                minutes = doctor.consultation_minutes or 15
                vals['stop_datetime'] = fields.Datetime.to_string(start + timedelta(minutes=minutes))
            if not vals.get('fee') and vals.get('doctor_id'):
                doctor = self.env['rn.hms.doctor'].browse(vals['doctor_id'])
                vals['fee'] = doctor.consulting_fee or 0.0
        return super().create(vals_list)

    def action_confirm(self):
        return self.env['rn.hms.appointment.service'].confirm(self)

    def action_start_consult(self):
        self.write({'state': 'in_consult'})
        return True

    def action_done(self):
        self.write({'state': 'done'})
        return True

    def action_cancel(self):
        self.write({'state': 'cancel'})
        self.env['rn.hms.notification.service'].notify_appointment_cancelled(self)
        return True

    def action_no_show(self):
        self.write({'state': 'no_show'})
        return True
