# -*- coding: utf-8 -*-

from odoo import api, fields, models


class RnVetOwner(models.Model):
    _name = 'rn.vet.owner'
    _description = 'Pet Owner'
    _inherit = ['mail.thread']
    _order = 'name'

    name = fields.Char(required=True, tracking=True)
    mobile = fields.Char(index=True)
    email = fields.Char()
    address = fields.Text()
    emergency_contact = fields.Char()
    partner_id = fields.Many2one('res.partner')
    pet_ids = fields.One2many('rn.vet.pet', 'owner_id')
    pet_count = fields.Integer(compute='_compute_pet_count')
    active = fields.Boolean(default=True)
    company_id = fields.Many2one(
        'res.company',
        required=True,
        default=lambda self: self.env.company,
        index=True,
    )

    @api.depends('pet_ids')
    def _compute_pet_count(self):
        for owner in self:
            owner.pet_count = len(owner.pet_ids)
