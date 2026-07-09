# -*- coding: utf-8 -*-

from odoo import fields, models


class RnHotelGuest(models.Model):
    _name = 'rn.hotel.guest'
    _description = 'Hotel Guest'
    _inherit = ['mail.thread']
    _order = 'name'

    name = fields.Char(required=True, tracking=True)
    partner_id = fields.Many2one('res.partner')
    mobile = fields.Char()
    email = fields.Char()
    id_type = fields.Selection(
        [('passport', 'Passport'), ('aadhaar', 'Aadhaar'), ('driving', 'Driving License'), ('other', 'Other')],
    )
    id_number = fields.Char(string='ID Number')
    nationality = fields.Char()
    vip = fields.Boolean(string='VIP Guest')
    note = fields.Text()
    reservation_ids = fields.One2many('rn.hotel.reservation', 'guest_id')
    company_id = fields.Many2one(
        'res.company',
        required=True,
        default=lambda self: self.env.company,
        index=True,
    )
