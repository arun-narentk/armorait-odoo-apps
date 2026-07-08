# -*- coding: utf-8 -*-
"""Doctor / consultant profiles."""

from odoo import fields, models


class RnHmsDoctor(models.Model):
    """Doctor working at the hospital or clinic."""

    _name = 'rn.hms.doctor'
    _description = 'HMS Doctor'
    _inherit = ['mail.thread']
    _order = 'name'

    name = fields.Char(required=True, tracking=True)
    active = fields.Boolean(default=True)
    employee_id = fields.Many2one('hr.employee', string='Linked Employee')
    partner_id = fields.Many2one('res.partner', string='Contact')
    user_id = fields.Many2one('res.users', string='Portal / User')
    specialization = fields.Char(tracking=True)
    registration_no = fields.Char(string='Registration No', index=True)
    department_ids = fields.Many2many(
        'rn.hms.department',
        'rn_hms_doctor_department_rel',
        'doctor_id',
        'department_id',
        string='Departments',
    )
    consulting_fee = fields.Monetary(currency_field='currency_id')
    currency_id = fields.Many2one(
        'res.currency',
        default=lambda self: self.env.company.currency_id,
    )
    consultation_minutes = fields.Integer(default=15)
    color = fields.Integer()
    company_id = fields.Many2one(
        'res.company',
        required=True,
        default=lambda self: self.env.company,
        index=True,
    )
    note = fields.Text()
