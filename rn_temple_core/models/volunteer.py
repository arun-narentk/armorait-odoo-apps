# -*- coding: utf-8 -*-

from odoo import fields, models


class RnTempleVolunteer(models.Model):
    _name = 'rn.temple.volunteer'
    _description = 'Temple Volunteer'
    _order = 'name'

    name = fields.Char(required=True)
    mobile = fields.Char()
    email = fields.Char()
    skills = fields.Char()
    employee_id = fields.Many2one('hr.employee')
    festival_ids = fields.Many2many('rn.temple.festival', string='Festivals')
    annadhanam_ids = fields.Many2many('rn.temple.annadhanam', string='Annadhanam Events')
    active = fields.Boolean(default=True)
    company_id = fields.Many2one(
        'res.company',
        required=True,
        default=lambda self: self.env.company,
        index=True,
    )
