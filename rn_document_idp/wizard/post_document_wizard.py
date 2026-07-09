# -*- coding: utf-8 -*-

from odoo import fields, models


class RnDocumentIdpPostWizard(models.TransientModel):
    _name = 'rn.document.idp.post.wizard'
    _description = 'Post Document to ERP'

    document_id = fields.Many2one('rn.document.idp.document', required=True)
    note = fields.Text()

    def action_confirm_post(self):
        self.ensure_one()
        if self.note:
            self.document_id.message_post(body=self.note)
        return self.document_id.action_post_to_erp()
