# -*- coding: utf-8 -*-
import base64
import json

from odoo import fields, models
from odoo.exceptions import UserError


class FilterImportExportWizard(models.TransientModel):
    _name = 'rn.filter.import.export.wizard'
    _description = 'Filter Import Export Wizard'

    mode = fields.Selection(
        [('export', 'Export'), ('import', 'Import')],
        required=True,
        default='export',
    )
    filter_ids = fields.Many2many('ir.filters', string='Filters')
    import_mode = fields.Selection(
        [('merge', 'Merge / Update'), ('skip_existing', 'Skip Existing')],
        default='merge',
    )
    json_file = fields.Binary(string='JSON File')
    json_filename = fields.Char(default='filters_export.json')
    export_data = fields.Text(readonly=True)

    def action_export(self):
        self.ensure_one()
        filters = self.filter_ids or self.env['ir.filters'].search([
            ('rn_owner_id', '=', self.env.user.id),
        ])
        if not filters:
            raise UserError('No filters selected for export.')
        payload = self.env['rn.filter.service'].export_filters(filters)
        content = json.dumps(payload, indent=2)
        self.write({
            'export_data': content,
            'json_file': base64.b64encode(content.encode('utf-8')),
            'json_filename': 'rn_filter_manager_export.json',
        })
        return {
            'type': 'ir.actions.act_window',
            'res_model': self._name,
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'new',
        }

    def action_import(self):
        self.ensure_one()
        if not self.json_file:
            raise UserError('Upload a JSON export file first.')
        raw = base64.b64decode(self.json_file).decode('utf-8')
        payload = json.loads(raw)
        created = self.env['rn.filter.service'].import_filters(payload, mode=self.import_mode)
        return {
            'type': 'ir.actions.act_window',
            'name': 'Imported Filters',
            'res_model': 'ir.filters',
            'view_mode': 'list,form',
            'domain': [('id', 'in', created.ids)],
        }
