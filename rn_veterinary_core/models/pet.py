# -*- coding: utf-8 -*-

from odoo import api, fields, models


class RnVetPet(models.Model):
    _name = 'rn.vet.pet'
    _description = 'Pet'
    _inherit = ['mail.thread']
    _order = 'name'

    name = fields.Char(required=True, tracking=True)
    owner_id = fields.Many2one('rn.vet.owner', required=True, index=True)
    species = fields.Selection(
        [
            ('dog', 'Dog'),
            ('cat', 'Cat'),
            ('bird', 'Bird'),
            ('rabbit', 'Rabbit'),
            ('livestock', 'Livestock'),
            ('other', 'Other'),
        ],
        default='dog',
        required=True,
    )
    breed = fields.Char()
    gender = fields.Selection([('male', 'Male'), ('female', 'Female'), ('unknown', 'Unknown')])
    color = fields.Char()
    date_of_birth = fields.Date()
    weight_kg = fields.Float(string='Weight (kg)')
    microchip = fields.Char(index=True)
    allergies = fields.Text()
    medical_history = fields.Text()
    active = fields.Boolean(default=True)
    vaccination_ids = fields.One2many('rn.vet.vaccination', 'pet_id')
    appointment_ids = fields.One2many('rn.vet.appointment', 'pet_id')
    medical_record_ids = fields.One2many('rn.vet.medical.record', 'pet_id')
    company_id = fields.Many2one(related='owner_id.company_id', store=True, index=True)

    @api.onchange('weight_kg')
    def _onchange_weight(self):
        if self.weight_kg and self.weight_kg < 0:
            self.weight_kg = 0.0
