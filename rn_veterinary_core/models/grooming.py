# -*- coding: utf-8 -*-

from odoo import fields, models


class RnVetGrooming(models.Model):
    _name = 'rn.vet.grooming'
    _description = 'Grooming Appointment'
    _order = 'grooming_date desc'

    name = fields.Char(required=True)
    pet_id = fields.Many2one('rn.vet.pet', required=True, index=True)
    grooming_date = fields.Datetime(required=True)
    service_type = fields.Selection(
        [
            ('bath', 'Bath'),
            ('haircut', 'Haircut'),
            ('nail_trim', 'Nail Trimming'),
            ('spa', 'Spa Package'),
        ],
        default='bath',
        required=True,
    )
    amount = fields.Float()
    state = fields.Selection(
        [('scheduled', 'Scheduled'), ('done', 'Done'), ('cancelled', 'Cancelled')],
        default='scheduled',
    )
    note = fields.Text()
    company_id = fields.Many2one(related='pet_id.company_id', store=True, index=True)
