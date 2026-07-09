# -*- coding: utf-8 -*-

from odoo import fields, models


class RnHospitalDoctorSchedule(models.Model):
    _name = 'rn.hospital.doctor.schedule'
    _description = 'Doctor Schedule Slot'
    _order = 'weekday, start_hour'

    doctor_id = fields.Many2one('hr.employee', required=True, index=True, domain=[('is_doctor', '=', True)])
    department_id = fields.Many2one('rn.hospital.department')
    weekday = fields.Selection(
        [
            ('0', 'Monday'), ('1', 'Tuesday'), ('2', 'Wednesday'),
            ('3', 'Thursday'), ('4', 'Friday'), ('5', 'Saturday'), ('6', 'Sunday'),
        ],
        required=True,
    )
    start_hour = fields.Float(required=True)
    end_hour = fields.Float(required=True)
    slot_minutes = fields.Integer(default=15)
    max_patients = fields.Integer(default=20)
    active = fields.Boolean(default=True)
    company_id = fields.Many2one(
        'res.company',
        required=True,
        default=lambda self: self.env.company,
        index=True,
    )
