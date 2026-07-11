# -*- coding: utf-8 -*-

from odoo import _, fields, models


class RnAttachmentSearchWizard(models.TransientModel):
    _name = 'rn.attachment.search.wizard'
    _description = 'Attachment OCR Search Wizard'

    query = fields.Char(string='Search Text', required=True)
    result_ids = fields.Many2many('ir.attachment', string='Results', readonly=True)
    result_count = fields.Integer(string='Matches', readonly=True)

    def action_search(self):
        self.ensure_one()
        results = self.env['rn.attachment.ocr.service'].search_attachments(self.query, limit=50)
        attachment_ids = [row['id'] for row in results]
        self.write({
            'result_ids': [(6, 0, attachment_ids)],
            'result_count': len(attachment_ids),
        })
        return {
            'type': 'ir.actions.act_window',
            'name': _('OCR Search Results'),
            'res_model': 'ir.attachment',
            'view_mode': 'list,form',
            'domain': [('id', 'in', attachment_ids)],
            'context': {'create': False},
        }
