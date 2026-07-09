# -*- coding: utf-8 -*-

from odoo import api, fields, models


class RnSchoolAdmissionEnquiry(models.Model):
    _name = 'rn.school.admission.enquiry'
    _description = 'Admission Enquiry'
    _inherit = ['mail.thread']
    _order = 'create_date desc'

    name = fields.Char(readonly=True, copy=False, default='New')
    applicant_name = fields.Char(required=True)
    parent_name = fields.Char()
    mobile = fields.Char(required=True)
    email = fields.Char()
    grade_applied = fields.Integer(string='Grade Applied')
    source = fields.Selection(
        [('walkin', 'Walk-in'), ('website', 'Website'), ('referral', 'Referral'), ('campaign', 'Campaign')],
        default='walkin',
    )
    state = fields.Selection(
        [('new', 'New'), ('contacted', 'Contacted'), ('converted', 'Converted'), ('lost', 'Lost')],
        default='new',
        tracking=True,
    )
    note = fields.Text()
    application_id = fields.Many2one('rn.school.admission.application', copy=False)
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
                vals['name'] = seq.next_by_code('rn.school.admission.enquiry') or 'ENQ'
        return super().create(vals_list)

    def action_convert_application(self):
        self.ensure_one()
        app = self.env['rn.school.admission.application'].create({
            'enquiry_id': self.id,
            'applicant_name': self.applicant_name,
            'parent_name': self.parent_name,
            'mobile': self.mobile,
            'email': self.email,
            'grade_applied': self.grade_applied,
            'state': 'application',
        })
        self.write({'state': 'converted', 'application_id': app.id})
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'rn.school.admission.application',
            'res_id': app.id,
            'view_mode': 'form',
            'target': 'current',
        }
