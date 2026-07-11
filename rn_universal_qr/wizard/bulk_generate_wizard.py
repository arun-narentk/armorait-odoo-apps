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

# -*- coding: utf-8 -*-

from odoo import fields, models, _
from odoo.exceptions import UserError


class RnQrBulkGenerateWizard(models.TransientModel):
    _name = 'rn.qr.bulk.generate.wizard'
    _description = 'Bulk QR Generation Wizard'

    res_model = fields.Char(required=True)
    res_ids = fields.Text(required=True, help='Comma-separated record IDs')
    template_id = fields.Many2one('rn.qr.template', string='Template')
    payload_type = fields.Selection(
        selection=lambda self: self.env['rn.qr.record']._selection_payload_type(),
    )
    action_type = fields.Selection(
        selection=lambda self: self.env['rn.qr.record']._selection_action_type(),
    )

    def action_generate_zip(self):
        self.ensure_one()
        try:
            ids = [int(x.strip()) for x in self.res_ids.split(',') if x.strip()]
        except ValueError as exc:
            raise UserError(_('Invalid record IDs.')) from exc
        values = {}
        if self.template_id:
            values.update({
                'template_id': self.template_id.id,
                'qr_size': self.template_id.qr_size,
                'qr_color': self.template_id.qr_color,
                'custom_color': self.template_id.custom_color,
                'ecc_level': self.template_id.ecc_level,
                'use_logo': self.template_id.use_logo,
                'payload_type': self.template_id.payload_type,
                'action_type': self.template_id.action_type,
            })
        if self.payload_type:
            values['payload_type'] = self.payload_type
        if self.action_type:
            values['action_type'] = self.action_type
        return self.env['rn.qr.service'].bulk_generate_zip(self.res_model, ids, values)
