# -*- coding: utf-8 -*-
"""Batch name generation from list views."""

import base64
import csv
import io

from odoo import fields, models, _


class RnNameBatchWizard(models.TransientModel):
    _name = 'rn.name.batch.wizard'
    _description = 'Batch Name Generator Wizard'

    res_model = fields.Char(required=True)
    res_ids = fields.Char(
        string='Record IDs',
        help='Comma-separated record IDs from the list selection.',
    )
    max_suggestions = fields.Integer(default=3)
    result_ids = fields.One2many(
        'rn.name.batch.wizard.line',
        'wizard_id',
        string='Results',
        readonly=True,
    )
    export_file = fields.Binary(readonly=True)
    export_filename = fields.Char(readonly=True)
    state = fields.Selection(
        [('draft', 'Draft'), ('done', 'Done')],
        default='draft',
    )

    def action_generate(self):
        self.ensure_one()
        service = self.env['rn.name.generator.service']
        ids = [int(x) for x in (self.res_ids or '').split(',') if x.strip().isdigit()]
        self.result_ids.unlink()
        lines = []
        for row in service.batch_generate(self.res_model, ids, max_count=self.max_suggestions):
            lines.append((0, 0, row))
        self.write({
            'result_ids': lines,
            'state': 'done',
        })
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'rn.name.batch.wizard',
            'view_mode': 'form',
            'res_id': self.id,
            'target': 'new',
        }

    def action_export_csv(self):
        self.ensure_one()
        buffer = io.StringIO()
        writer = csv.writer(buffer)
        writer.writerow(['Record ID', 'Current Name', 'Top Suggestion', 'All Suggestions'])
        for line in self.result_ids:
            writer.writerow([
                line.res_id,
                line.current_name,
                line.suggested_name,
                line.all_suggestions,
            ])
        payload = base64.b64encode(buffer.getvalue().encode('utf-8'))
        self.write({
            'export_file': payload,
            'export_filename': 'name_suggestions.csv',
        })
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'rn.name.batch.wizard',
            'view_mode': 'form',
            'res_id': self.id,
            'target': 'new',
        }


class RnNameBatchWizardLine(models.TransientModel):
    _name = 'rn.name.batch.wizard.line'
    _description = 'Batch Name Generator Line'

    wizard_id = fields.Many2one('rn.name.batch.wizard', required=True, ondelete='cascade')
    res_id = fields.Integer(required=True)
    current_name = fields.Char()
    suggested_name = fields.Char()
    all_suggestions = fields.Char()
