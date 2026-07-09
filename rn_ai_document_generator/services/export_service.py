# -*- coding: utf-8 -*-
"""CSV export of document metrics."""

import base64

from odoo import fields, models


class RnAiDocumentExportService(models.AbstractModel):
    _name = 'rn.ai.document.export.service'
    _description = 'AI Document Export Service'

    def export_documents_csv(self, company_id=None, limit=500):
        company_id = company_id or self.env.company.id
        docs = self.env['rn.ai.document'].search([('company_id', '=', company_id)], limit=limit)
        lines = ['name,type,state,language,style,partner,employee']
        for doc in docs:
            lines.append('%s,%s,%s,%s,%s,%s,%s' % (
                doc.name,
                doc.type_id.name if doc.type_id else '',
                doc.state,
                doc.language,
                doc.style,
                doc.partner_id.name if doc.partner_id else '',
                doc.employee_id.name if doc.employee_id else '',
            ))
        content = chr(10).join(lines)
        attachment = self.env['ir.attachment'].create({
            'name': 'ai_documents.csv',
            'type': 'binary',
            'datas': base64.b64encode(content.encode('utf-8')),
            'mimetype': 'text/csv',
        })
        return {
            'type': 'ir.actions.act_url',
            'url': '/web/content/%s?download=true' % attachment.id,
            'target': 'self',
        }
