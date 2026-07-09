# -*- coding: utf-8 -*-

from odoo import models


class RnDentalChartingService(models.AbstractModel):
    _name = 'rn.dental.charting.service'
    _description = 'Dental Charting Service'

    def set_tooth_condition(self, patient_id, tooth_number, condition, surface=None, note=None):
        Tooth = self.env['rn.dental.tooth.record']
        rec = Tooth.search([
            ('patient_id', '=', patient_id),
            ('tooth_number', '=', str(tooth_number)),
        ], limit=1)
        vals = {
            'patient_id': patient_id,
            'tooth_number': str(tooth_number),
            'condition': condition,
            'surface': surface,
            'note': note,
        }
        if rec:
            rec.write(vals)
            return rec.id
        return Tooth.create(vals).id

    def get_chart_summary(self, patient_id):
        records = self.env['rn.dental.tooth.record'].search([('patient_id', '=', patient_id)])
        summary = {}
        for rec in records:
            summary[rec.tooth_number] = rec.condition
        return summary
