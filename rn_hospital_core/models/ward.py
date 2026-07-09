# -*- coding: utf-8 -*-

from odoo import fields, models


class RnHospitalWard(models.Model):
    _name = 'rn.hospital.ward'
    _description = 'Hospital Ward'
    _order = 'name'

    name = fields.Char(required=True)
    code = fields.Char()
    ward_type = fields.Selection(
        [('general', 'General'), ('icu', 'ICU'), ('private', 'Private'), ('daycare', 'Day Care')],
        default='general',
    )
    bed_ids = fields.One2many('rn.hospital.bed', 'ward_id')
    bed_count = fields.Integer(compute='_compute_bed_count')
    company_id = fields.Many2one(
        'res.company',
        required=True,
        default=lambda self: self.env.company,
        index=True,
    )

    def _compute_bed_count(self):
        for ward in self:
            ward.bed_count = len(ward.bed_ids)


class RnHospitalBed(models.Model):
    _name = 'rn.hospital.bed'
    _description = 'Hospital Bed'

    name = fields.Char(required=True)
    ward_id = fields.Many2one('rn.hospital.ward', required=True, ondelete='cascade', index=True)
    state = fields.Selection(
        [('available', 'Available'), ('occupied', 'Occupied'), ('maintenance', 'Maintenance')],
        default='available',
    )
    daily_charge = fields.Float(string='Daily Room Charge')
    company_id = fields.Many2one(related='ward_id.company_id', store=True, index=True)
