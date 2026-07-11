# -*- coding: utf-8 -*-
"""Popup wizard to pick a suggested name."""

from odoo import api, fields, models, _


class RnNameGeneratorWizard(models.TransientModel):
    _name = 'rn.name.generator.wizard'
    _description = 'Name Generator Wizard'

    res_model = fields.Char(required=True)
    res_id = fields.Integer(required=True)
    current_name = fields.Char(string='Current', readonly=True)
    preview_name = fields.Char(string='Live Preview', readonly=True)
    line_ids = fields.One2many(
        'rn.name.generator.wizard.line',
        'wizard_id',
        string='Suggestions',
    )
    selected_line_id = fields.Many2one(
        'rn.name.generator.wizard.line',
        string='Selected Suggestion',
    )

    @api.model
    def open_for_record(self, res_model, res_id):
        service = self.env['rn.name.generator.service']
        record = service._get_target_record(res_model, res_id)
        suggestions = service.generate_for_record(res_model, res_id)
        lines = [
            (0, 0, {
                'sequence': index + 1,
                'suggested_name': row['name'],
                'score': row['score'],
                'template_id': row.get('template_id') or False,
                'is_selected': index == 0,
            })
            for index, row in enumerate(suggestions)
        ]
        wizard = self.create({
            'res_model': res_model,
            'res_id': res_id,
            'current_name': service._current_name(record),
            'preview_name': suggestions[0]['name'] if suggestions else service._current_name(record),
            'line_ids': lines,
            'selected_line_id': False,
        })
        if wizard.line_ids:
            wizard.selected_line_id = wizard.line_ids[0].id
        return {
            'type': 'ir.actions.act_window',
            'name': _('Suggest Name'),
            'res_model': 'rn.name.generator.wizard',
            'view_mode': 'form',
            'res_id': wizard.id,
            'target': 'new',
        }

    def action_refresh(self):
        self.ensure_one()
        return self.open_for_record(self.res_model, self.res_id)

    def action_use_selected(self):
        self.ensure_one()
        line = self.selected_line_id or (self.line_ids[:1] if self.line_ids else False)
        if not line:
            return {'type': 'ir.actions.act_window_close'}
        self.env['rn.name.generator.service'].apply_selected_name(
            self.res_model,
            self.res_id,
            line.suggested_name,
        )
        return {'type': 'ir.actions.act_window_close'}


class RnNameGeneratorWizardLine(models.TransientModel):
    _name = 'rn.name.generator.wizard.line'
    _description = 'Name Generator Wizard Line'
    _order = 'sequence, score desc, id'

    wizard_id = fields.Many2one('rn.name.generator.wizard', required=True, ondelete='cascade')
    sequence = fields.Integer(default=1)
    suggested_name = fields.Char(required=True)
    score = fields.Float()
    template_id = fields.Many2one('rn.name.template', readonly=True)
    is_selected = fields.Boolean()

    def action_select_line(self):
        self.ensure_one()
        self.wizard_id.write({'selected_line_id': self.id})
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'rn.name.generator.wizard',
            'view_mode': 'form',
            'res_id': self.wizard_id.id,
            'target': 'new',
        }
