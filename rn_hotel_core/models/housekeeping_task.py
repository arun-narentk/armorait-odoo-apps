# -*- coding: utf-8 -*-

from odoo import fields, models


class RnHotelHousekeepingTask(models.Model):
    _name = 'rn.hotel.housekeeping.task'
    _description = 'Housekeeping Task'
    _inherit = ['mail.thread']
    _order = 'priority desc, create_date'

    name = fields.Char(required=True)
    room_id = fields.Many2one('rn.hotel.room', required=True, index=True)
    assigned_to = fields.Many2one('hr.employee', string='Housekeeper')
    supervisor_id = fields.Many2one('hr.employee', string='Supervisor')
    state = fields.Selection(
        [
            ('dirty', 'Dirty'),
            ('assigned', 'Assigned'),
            ('in_progress', 'In Progress'),
            ('inspection', 'Inspection'),
            ('done', 'Done'),
        ],
        default='dirty',
        tracking=True,
    )
    priority = fields.Selection([('0', 'Normal'), ('1', 'High'), ('2', 'Urgent')], default='0')
    note = fields.Text()
    company_id = fields.Many2one(
        'res.company',
        required=True,
        default=lambda self: self.env.company,
        index=True,
    )
