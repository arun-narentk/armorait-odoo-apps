# -*- coding: utf-8 -*-

from odoo import api, fields, models


class RnHospitalEmrEncounter(models.Model):
    """Consultation / visit EMR record."""

    _name = 'rn.hospital.emr.encounter'
    _description = 'EMR Encounter'
    _inherit = ['mail.thread']
    _order = 'encounter_datetime desc'

    name = fields.Char(readonly=True, copy=False, default='New')
    patient_id = fields.Many2one('rn.hospital.patient', required=True, index=True)
    doctor_id = fields.Many2one('hr.employee', domain=[('is_doctor', '=', True)])
    appointment_id = fields.Many2one('rn.hospital.appointment')
    admission_id = fields.Many2one('rn.hospital.admission')
    department_id = fields.Many2one('rn.hospital.department')
    encounter_datetime = fields.Datetime(default=fields.Datetime.now, required=True)
    encounter_type = fields.Selection(
        [
            ('opd', 'OPD'),
            ('ipd', 'IPD'),
            ('emergency', 'Emergency'),
            ('tele', 'Teleconsultation'),
        ],
        default='opd',
    )
    state = fields.Selection(
        [('draft', 'Draft'), ('in_progress', 'In Progress'), ('signed', 'Signed')],
        default='draft',
        tracking=True,
    )
    chief_complaint = fields.Text()
    consultation_notes = fields.Html()
    ai_scribe_notes = fields.Html(string='AI Scribe Draft', readonly=True)
    diagnosis_ids = fields.One2many('rn.hospital.emr.diagnosis', 'encounter_id')
    prescription_ids = fields.One2many('rn.hospital.emr.prescription', 'encounter_id')
    discharge_summary = fields.Html()
    ai_discharge_draft = fields.Html(string='AI Discharge Draft', readonly=True)
    attachment_ids = fields.Many2many('ir.attachment', string='Reports / Images')
    company_id = fields.Many2one(
        'res.company',
        required=True,
        default=lambda self: self.env.company,
        index=True,
    )

    @api.model_create_multi
    def create(self, vals_list):
        seq = self.env['ir.sequence']
        for vals in vals_list:
            if vals.get('name', 'New') == 'New':
                vals['name'] = seq.next_by_code('rn.hospital.emr.encounter') or 'ENC'
        return super().create(vals_list)

    def action_generate_ai_scribe(self):
        for rec in self:
            rec.ai_scribe_notes = self.env['rn.hospital.insight.service'].draft_scribe(rec.id)

    def action_generate_discharge_summary(self):
        for rec in self:
            rec.ai_discharge_draft = self.env['rn.hospital.insight.service'].draft_discharge(rec.id)


class RnHospitalEmrDiagnosis(models.Model):
    _name = 'rn.hospital.emr.diagnosis'
    _description = 'EMR Diagnosis'

    encounter_id = fields.Many2one('rn.hospital.emr.encounter', required=True, ondelete='cascade')
    code = fields.Char(string='ICD Code')
    name = fields.Char(required=True)
    note = fields.Text()
