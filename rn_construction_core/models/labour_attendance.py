# -*- coding: utf-8 -*-

from odoo import fields, models


class RnConstructionLabourAttendance(models.Model):
    _name = 'rn.construction.labour.attendance'
    _description = 'Site Labour Attendance'
    _order = 'attendance_date desc'

    site_id = fields.Many2one('rn.construction.site', required=True, index=True)
    contractor_id = fields.Many2one('res.partner', string='Contractor')
    worker_name = fields.Char(required=True)
    attendance_date = fields.Date(required=True, default=fields.Date.context_today, index=True)
    hours = fields.Float(default=8.0)
    overtime_hours = fields.Float()
    daily_wage = fields.Float()
    state = fields.Selection([('present', 'Present'), ('absent', 'Absent'), ('half', 'Half Day')], default='present')
    company_id = fields.Many2one(related='site_id.company_id', store=True, index=True)
