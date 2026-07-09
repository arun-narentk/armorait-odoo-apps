# -*- coding: utf-8 -*-

from odoo import api, fields, models


class RnHospitalAdmission(models.Model):
    _name = 'rn.hospital.admission'
    _description = 'Inpatient Admission'
    _inherit = ['mail.thread']
    _order = 'admission_datetime desc'

    name = fields.Char(readonly=True, copy=False, default='New')
    patient_id = fields.Many2one('rn.hospital.patient', required=True, index=True)
    doctor_id = fields.Many2one('hr.employee', domain=[('is_doctor', '=', True)])
    bed_id = fields.Many2one('rn.hospital.bed')
    ward_id = fields.Many2one(related='bed_id.ward_id', store=True)
    admission_datetime = fields.Datetime(default=fields.Datetime.now, required=True)
    discharge_datetime = fields.Datetime()
    state = fields.Selection(
        [
            ('admitted', 'Admitted'),
            ('discharged', 'Discharged'),
            ('transferred', 'Transferred'),
            ('cancelled', 'Cancelled'),
        ],
        default='admitted',
        tracking=True,
    )
    diagnosis = fields.Text()
    nursing_notes = fields.Html()
    diet_plan = fields.Text()
    encounter_ids = fields.One2many('rn.hospital.emr.encounter', 'admission_id')
    company_id = fields.Many2one(
        'res.company',
        required=True,
        default=lambda self: self.env.company,
        index=True,
    )

    @api.model_create_multi
    def create(self, vals_list):
        seq = self.env['ir.sequence']
        Bed = self.env['rn.hospital.bed']
        for vals in vals_list:
            if vals.get('name', 'New') == 'New':
                vals['name'] = seq.next_by_code('rn.hospital.admission') or 'ADM'
        records = super().create(vals_list)
        for rec in records:
            if rec.bed_id:
                Bed.browse(rec.bed_id.id).state = 'occupied'
        return records

    def action_discharge(self):
        Bed = self.env['rn.hospital.bed']
        for rec in self:
            rec.write({
                'state': 'discharged',
                'discharge_datetime': fields.Datetime.now(),
            })
            if rec.bed_id:
                Bed.browse(rec.bed_id.id).state = 'available'
