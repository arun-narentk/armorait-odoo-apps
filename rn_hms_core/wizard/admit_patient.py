# -*- coding: utf-8 -*-
"""Simple bed allocation wizard (IPD foundation)."""

from odoo import fields, models


class RnHmsAdmitPatientWizard(models.TransientModel):
    """Allocate an available bed to a patient."""

    _name = 'rn.hms.admit.patient.wizard'
    _description = 'Admit Patient Wizard'

    patient_id = fields.Many2one('rn.hms.patient', required=True)
    bed_id = fields.Many2one(
        'rn.hms.bed',
        required=True,
        domain="[('state', '=', 'available')]",
    )
    note = fields.Text()

    def action_admit(self):
        self.ensure_one()
        self.env['rn.hms.bed.service'].allocate(self.bed_id, self.patient_id)
        if self.note:
            self.bed_id.note = self.note
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'rn.hms.bed',
            'res_id': self.bed_id.id,
            'view_mode': 'form',
            'target': 'current',
        }
