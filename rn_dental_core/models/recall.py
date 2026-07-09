# -*- coding: utf-8 -*-

from odoo import fields, models


class RnDentalRecall(models.Model):
    _name = 'rn.dental.recall'
    _description = 'Patient Recall'
    _order = 'due_date'

    patient_id = fields.Many2one('rn.dental.patient', required=True, ondelete='cascade', index=True)
    recall_type = fields.Selection(
        [
            ('checkup', 'Six-Month Check-up'),
            ('hygiene', 'Hygiene'),
            ('orthodontic', 'Orthodontic Review'),
            ('implant', 'Implant Follow-up'),
            ('treatment', 'Treatment Follow-up'),
        ],
        default='checkup',
        required=True,
    )
    due_date = fields.Date(required=True, index=True)
    state = fields.Selection(
        [('pending', 'Pending'), ('scheduled', 'Scheduled'), ('done', 'Done'), ('skipped', 'Skipped')],
        default='pending',
    )
    note = fields.Text()
    company_id = fields.Many2one(related='patient_id.company_id', store=True, index=True)
