# -*- coding: utf-8 -*-
from odoo import fields, models


class BulkGenerateWizard(models.TransientModel):
    _name = 'rn.qr.bulk.generate.wizard'
    _description = 'Bulk Generate QR Wizard'

    model_id = fields.Many2one('ir.model', required=True, domain=[('transient', '=', False)])
    limit = fields.Integer(default=100)
    include_archived = fields.Boolean(default=False)
    zip_file = fields.Binary(readonly=True)
    zip_filename = fields.Char(readonly=True, default='qr_codes.zip')

    def action_generate(self):
        self.ensure_one()
        model_name = self.model_id.model
        domain = []
        if not self.include_archived and 'active' in self.env[model_name]._fields:
            domain.append(('active', '=', True))
        records = self.env[model_name].search(domain, limit=self.limit)
        payload = self.env['rn.qr.service'].export_bulk_zip(records)
        self.write({
            'zip_file': payload['content'],
            'zip_filename': payload['filename'],
        })
        return {
            'type': 'ir.actions.act_window',
            'res_model': self._name,
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'new',
        }
