# -*- coding: utf-8 -*-

from odoo import fields, models


TOOTH_NUMBERS = [(str(n), str(n)) for n in range(11, 19)] + [(str(n), str(n)) for n in range(21, 29)] + \
                [(str(n), str(n)) for n in range(31, 39)] + [(str(n), str(n)) for n in range(41, 49)]


class RnDentalToothRecord(models.Model):
    _name = 'rn.dental.tooth.record'
    _description = 'Tooth Chart Record'
    _order = 'tooth_number'

    patient_id = fields.Many2one('rn.dental.patient', required=True, ondelete='cascade', index=True)
    tooth_number = fields.Selection(selection=TOOTH_NUMBERS, required=True, string='Tooth (FDI)')
    condition = fields.Selection(
        [
            ('healthy', 'Healthy'),
            ('missing', 'Missing'),
            ('filled', 'Filled'),
            ('crown', 'Crown'),
            ('bridge', 'Bridge'),
            ('implant', 'Implant'),
            ('root_canal', 'Root Canal'),
            ('decay', 'Decay'),
            ('gum_issue', 'Gum Issue'),
        ],
        default='healthy',
        required=True,
    )
    surface = fields.Char(help='Mesial, distal, occlusal, etc.')
    note = fields.Text()
    last_treatment_date = fields.Date()
    company_id = fields.Many2one(related='patient_id.company_id', store=True, index=True)

    _sql_constraints = [
        ('patient_tooth_uniq', 'unique(patient_id, tooth_number)', 'Each tooth can have only one chart record per patient.'),
    ]
