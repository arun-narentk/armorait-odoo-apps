# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, models


class IrAttachment(models.Model):
    _inherit = 'ir.attachment'

    @api.model_create_multi
    def create(self, vals_list):
        attachments = super().create(vals_list)
        for att in attachments:
            if (
                att.res_model == 'hr.applicant'
                and att.res_id
                and att.mimetype == 'application/pdf'
            ):
                applicant = self.env['hr.applicant'].browse(att.res_id)
                if applicant.exists() and applicant.parsing_status in ('draft', 'error'):
                    applicant._trigger_resume_parsing(att)
        return attachments
