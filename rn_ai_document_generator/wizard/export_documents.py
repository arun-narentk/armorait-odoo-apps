# -*- coding: utf-8 -*-
"""Export documents CSV."""

from odoo import fields, models


class RnAiDocumentExportWizard(models.TransientModel):
    _name = 'rn.ai.document.export.wizard'
    _description = 'Export AI Documents'

    company_id = fields.Many2one(
        'res.company',
        required=True,
        default=lambda self: self.env.company,
    )
    limit = fields.Integer(default=500)

    def action_export(self):
        self.ensure_one()
        return self.env['rn.ai.document.export.service'].export_documents_csv(
            company_id=self.company_id.id,
            limit=self.limit,
        )
