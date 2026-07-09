# -*- coding: utf-8 -*-
"""Wards for IPD bed management."""

from odoo import api, fields, models


class RnHmsWard(models.Model):
    """Ward containing one or more beds."""

    _name = 'rn.hms.ward'
    _description = 'HMS Ward'
    _order = 'name'

    name = fields.Char(required=True)
    code = fields.Char(index=True)
    active = fields.Boolean(default=True)
    department_id = fields.Many2one('rn.hms.department')
    ward_type = fields.Selection(
        selection=[
            ('general', 'General'),
            ('icu', 'ICU'),
            ('nicu', 'NICU'),
            ('private', 'Private'),
            ('semi', 'Semi Private'),
            ('day_care', 'Day Care'),
        ],
        default='general',
        required=True,
    )
    bed_ids = fields.One2many('rn.hms.bed', 'ward_id', string='Beds')
    bed_count = fields.Integer(compute='_compute_bed_stats')
    occupied_count = fields.Integer(compute='_compute_bed_stats')
    company_id = fields.Many2one(
        'res.company',
        required=True,
        default=lambda self: self.env.company,
        index=True,
    )
    note = fields.Text()

    @api.depends('bed_ids', 'bed_ids.state')
    def _compute_bed_stats(self):
        for ward in self:
            beds = ward.bed_ids
            ward.bed_count = len(beds)
            ward.occupied_count = len(beds.filtered(lambda b: b.state == 'occupied'))
