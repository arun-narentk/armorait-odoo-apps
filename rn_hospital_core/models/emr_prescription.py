# -*- coding: utf-8 -*-

from odoo import fields, models


class RnHospitalEmrPrescription(models.Model):
    _name = 'rn.hospital.emr.prescription'
    _description = 'EMR Prescription Line'
    _order = 'sequence, id'

    encounter_id = fields.Many2one('rn.hospital.emr.encounter', required=True, ondelete='cascade', index=True)
    sequence = fields.Integer(default=10)
    product_id = fields.Many2one('product.product', string='Medicine')
    medicine_name = fields.Char(required=True)
    dosage = fields.Char()
    frequency = fields.Char()
    duration_days = fields.Integer(string='Duration (days)')
    quantity = fields.Float(default=1.0)
    instructions = fields.Text()
    ai_warning = fields.Char(string='AI Interaction Warning', readonly=True)
