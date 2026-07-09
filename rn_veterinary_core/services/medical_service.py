# -*- coding: utf-8 -*-

from odoo import models


class RnVetMedicalService(models.AbstractModel):
    _name = 'rn.vet.medical.service'
    _description = 'Medical Record Service'

    def create_consultation(self, pet_id, diagnosis, prescription=None, veterinarian_id=None):
        pet = self.env['rn.vet.pet'].browse(pet_id)
        rec = self.env['rn.vet.medical.record'].create({
            'name': f'Consultation - {pet.name}',
            'pet_id': pet_id,
            'veterinarian_id': veterinarian_id,
            'diagnosis': diagnosis,
            'prescription': prescription,
        })
        return rec.id

    def attach_lab_result(self, pet_id, test_type, result_summary, name=None):
        pet = self.env['rn.vet.pet'].browse(pet_id)
        return self.env['rn.vet.lab.result'].create({
            'name': name or f'{test_type} - {pet.name}',
            'pet_id': pet_id,
            'test_type': test_type,
            'result_summary': result_summary,
        }).id
