# -*- coding: utf-8 -*-

from odoo import fields, models


class RnVetVaccination(models.Model):
    _name = 'rn.vet.vaccination'
    _description = 'Pet Vaccination'
    _order = 'administered_date desc'

    pet_id = fields.Many2one('rn.vet.pet', required=True, ondelete='cascade', index=True)
    vaccine_type_id = fields.Many2one('rn.vet.vaccine.type', required=True, index=True)
    administered_date = fields.Date(required=True, default=fields.Date.context_today)
    next_due_date = fields.Date(index=True)
    batch_number = fields.Char()
    veterinarian_id = fields.Many2one('hr.employee', string='Veterinarian')
    state = fields.Selection(
        [('done', 'Administered'), ('due', 'Due'), ('overdue', 'Overdue'), ('scheduled', 'Scheduled')],
        default='done',
    )
    note = fields.Text()
    company_id = fields.Many2one(related='pet_id.company_id', store=True, index=True)
