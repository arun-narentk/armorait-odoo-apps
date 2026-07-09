# -*- coding: utf-8 -*-

from odoo import fields, models


class RnVetMedicalRecord(models.Model):
    _name = 'rn.vet.medical.record'
    _description = 'Pet Medical Record'
    _inherit = ['mail.thread']
    _order = 'record_date desc'

    name = fields.Char(required=True)
    pet_id = fields.Many2one('rn.vet.pet', required=True, ondelete='cascade', index=True)
    record_date = fields.Datetime(default=fields.Datetime.now, required=True)
    veterinarian_id = fields.Many2one('hr.employee', string='Veterinarian')
    diagnosis = fields.Text()
    prescription = fields.Text()
    follow_up_plan = fields.Text()
    ai_note_draft = fields.Text(string='AI Note Draft', readonly=True)
    attachment_ids = fields.Many2many('ir.attachment', string='Imaging')
    company_id = fields.Many2one(related='pet_id.company_id', store=True, index=True)

    def action_generate_ai_note(self):
        for rec in self:
            rec.ai_note_draft = self.env['rn.vet.insight.service'].draft_clinical_note(rec.id)
