# -*- coding: utf-8 -*-

import base64

from odoo import _, fields, models


class RnFieldDiffExportWizard(models.TransientModel):
    _name = 'rn.field.diff.export.wizard'
    _description = 'Export Field Differences'

    model = fields.Char(required=True)
    res_id = fields.Integer(required=True)
    export_format = fields.Selection(
        selection=[
            ('csv', 'CSV'),
            ('pdf', 'PDF'),
        ],
        default='csv',
        required=True,
    )

    def action_export(self):
        self.ensure_one()
        diffs = self.env['rn.field.diff.service'].get_record_diffs(self.model, self.res_id)
        if self.export_format == 'pdf':
            report = self.env.ref('rn_field_diff.action_report_field_diff')
            return report.report_action(diffs)
        content = self.env['rn.field.diff.service'].export_csv(diffs.ids)
        attachment = self.env['ir.attachment'].create({
            'name': 'field_changes_%s_%s.csv' % (self.model.replace('.', '_'), self.res_id),
            'type': 'binary',
            'datas': base64.b64encode(content),
            'mimetype': 'text/csv',
        })
        return {
            'type': 'ir.actions.act_url',
            'url': '/web/content/%s?download=true' % attachment.id,
            'target': 'self',
        }
