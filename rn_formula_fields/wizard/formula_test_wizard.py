# -*- coding: utf-8 -*-

import json

from odoo import fields, models
from odoo.exceptions import ValidationError


class FormulaTestWizard(models.TransientModel):
    _name = 'rn.formula.test.wizard'
    _description = 'Formula Test Wizard'

    formula_id = fields.Many2one('rn.formula.field', required=True, readonly=True)
    values_json = fields.Text(
        string='Values (JSON)', default='{}',
        help='Provide formula input values as a JSON object.')
    result = fields.Char(readonly=True)
    error_message = fields.Text(readonly=True)

    def action_test(self):
        self.ensure_one()
        try:
            values = json.loads(self.values_json or '{}')
            if not isinstance(values, dict):
                raise ValidationError('Values must be a JSON object.')
            self.write({
                'result': str(self.formula_id._engine.evaluate(
                    self.formula_id.expression, values)),
                'error_message': False,
            })
        except (ValueError, ValidationError) as error:
            self.write({'result': False, 'error_message': str(error)})
        return {
            'type': 'ir.actions.act_window',
            'res_model': self._name,
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'new',
        }
