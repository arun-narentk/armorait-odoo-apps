# -*- coding: utf-8 -*-

from odoo import fields, models


class RnHotelMaintenanceRequest(models.Model):
    _name = 'rn.hotel.maintenance.request'
    _description = 'Maintenance Request'
    _inherit = ['mail.thread']
    _order = 'create_date desc'

    name = fields.Char(required=True)
    room_id = fields.Many2one('rn.hotel.room', index=True)
    category = fields.Selection(
        [
            ('hvac', 'HVAC'),
            ('plumbing', 'Plumbing'),
            ('electrical', 'Electrical'),
            ('furniture', 'Furniture'),
            ('other', 'Other'),
        ],
        default='other',
    )
    state = fields.Selection(
        [('open', 'Open'), ('in_progress', 'In Progress'), ('done', 'Done')],
        default='open',
        tracking=True,
    )
    assigned_to = fields.Many2one('hr.employee')
    description = fields.Text()
    company_id = fields.Many2one(
        'res.company',
        required=True,
        default=lambda self: self.env.company,
        index=True,
    )
