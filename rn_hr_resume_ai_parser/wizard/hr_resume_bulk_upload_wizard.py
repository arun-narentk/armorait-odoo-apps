# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import logging
from odoo import api, fields, models, _
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class HrResumeBulkUploadWizard(models.TransientModel):
    _name = 'hr.resume.bulk.upload.wizard'
    _description = 'Bulk Resume Upload'

    job_id = fields.Many2one(
        'hr.job',
        string='Job Position',
        help='Optional: assign all new applicants to this job.',
    )
    attachment_ids = fields.Many2many(
        'ir.attachment',
        'hr_resume_bulk_upload_attachment_rel',
        'wizard_id',
        'attachment_id',
        string='Resume PDFs',
        help='Upload one or more PDF resumes. One applicant will be created per file.',
    )
    state = fields.Selection([
        ('upload', 'Upload'),
        ('done', 'Done'),
    ], default='upload')
    result_count = fields.Integer(string='Applicants created', readonly=True)
    created_applicant_ids = fields.Many2many(
        'hr.applicant',
        'hr_resume_bulk_upload_applicant_rel',
        'wizard_id',
        'applicant_id',
        string='Created applicants',
        readonly=True,
    )
    result_message = fields.Html(string='Result', readonly=True)

    def action_confirm(self):
        self.ensure_one()
        if not self.attachment_ids:
            raise UserError(_('Please upload at least one PDF resume.'))
        pdfs = self.attachment_ids.filtered(lambda a: a.mimetype == 'application/pdf')
        if len(pdfs) != len(self.attachment_ids):
            raise UserError(_('All files must be PDFs.'))
        created = self.env['hr.applicant']
        for att in pdfs:
            name = (att.name or 'Resume').replace('.pdf', '').strip() or 'Resume'
            applicant = self.env['hr.applicant'].create({
                'partner_name': name[:256],
                'job_id': self.job_id.id if self.job_id else False,
            })
            new_att = att.copy({
                'res_model': 'hr.applicant',
                'res_id': applicant.id,
                'name': att.name,
            })
            applicant.write({'resume_attachment_id': new_att.id})
            applicant._trigger_resume_parsing(new_att)
            created |= applicant
        self.write({
            'state': 'done',
            'result_count': len(created),
            'created_applicant_ids': [(6, 0, created.ids)],
            'result_message': _(
                '<p>Created <strong>%s</strong> applicant(s). Parsing has been queued for each resume.</p>'
            ) % len(created),
        })
        return {
            'type': 'ir.actions.act_window',
            'res_model': self._name,
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'new',
        }

    def action_view_created(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Created Applicants'),
            'res_model': 'hr.applicant',
            'view_mode': 'list,form',
            'domain': [('id', 'in', self.created_applicant_ids.ids)],
            'context': {'create': False},
        }
