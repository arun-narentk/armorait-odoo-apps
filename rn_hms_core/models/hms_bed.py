# -*- coding: utf-8 -*-
"""Hospital beds with occupancy state."""

from odoo import fields, models


class RnHmsBed(models.Model):
    """Single bed inside a ward."""

    _name = 'rn.hms.bed'
    _description = 'HMS Bed'
    _order = 'name'

    name = fields.Char(required=True)
    code = fields.Char(index=True)
    active = fields.Boolean(default=True)
    ward_id = fields.Many2one('rn.hms.ward', required=True, ondelete='cascade', index=True)
    state = fields.Selection(
        selection=[
            ('available', 'Available'),
            ('occupied', 'Occupied'),
            ('reserved', 'Reserved'),
            ('cleaning', 'Cleaning'),
            ('maintenance', 'Maintenance'),
        ],
        default='available',
        required=True,
        index=True,
    )
    patient_id = fields.Many2one('rn.hms.patient', string='Current Patient')
    company_id = fields.Many2one(
        'res.company',
        related='ward_id.company_id',
        store=True,
        index=True,
    )
    note = fields.Text()

    def action_mark_available(self):
        self.write({'state': 'available', 'patient_id': False})
        return True

    def action_mark_cleaning(self):
        self.write({'state': 'cleaning'})
        return True
