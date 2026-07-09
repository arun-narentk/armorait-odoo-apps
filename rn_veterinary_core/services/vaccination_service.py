# -*- coding: utf-8 -*-

from dateutil.relativedelta import relativedelta

from odoo import fields, models


class RnVetVaccinationService(models.AbstractModel):
    _name = 'rn.vet.vaccination.service'
    _description = 'Vaccination Service'

    def administer(self, pet_id, vaccine_type_id, veterinarian_id=None, batch_number=None):
        vaccine = self.env['rn.vet.vaccine.type'].browse(vaccine_type_id)
        administered = fields.Date.context_today(self)
        next_due = administered + relativedelta(months=vaccine.interval_months or 12)
        rec = self.env['rn.vet.vaccination'].create({
            'pet_id': pet_id,
            'vaccine_type_id': vaccine_type_id,
            'administered_date': administered,
            'next_due_date': next_due,
            'veterinarian_id': veterinarian_id,
            'batch_number': batch_number,
            'state': 'done',
        })
        return rec.id

    def due_vaccinations(self, company_id=None, within_days=30):
        company_id = company_id or self.env.company.id
        cutoff = fields.Date.context_today(self) + relativedelta(days=within_days)
        return self.env['rn.vet.vaccination'].search([
            ('company_id', '=', company_id),
            ('next_due_date', '<=', cutoff),
            ('state', 'in', ('done', 'due', 'overdue')),
        ])

    def suggest_for_pet(self, pet_id):
        pet = self.env['rn.vet.pet'].browse(pet_id)
        vaccines = self.env['rn.vet.vaccine.type'].search([
            '|', ('species', '=', pet.species), ('species', '=', 'all'),
            ('active', '=', True),
        ])
        administered = self.env['rn.vet.vaccination'].search([
            ('pet_id', '=', pet_id),
            ('state', '=', 'done'),
        ]).mapped('vaccine_type_id').ids
        return vaccines.filtered(lambda v: v.id not in administered)
