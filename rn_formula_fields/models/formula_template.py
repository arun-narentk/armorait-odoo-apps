# -*- coding: utf-8 -*-

from odoo import fields, models


class FormulaTemplate(models.Model):
    _name = 'rn.formula.template'
    _description = 'Formula Template'
    _order = 'name'

    name = fields.Char(required=True, translate=True)
    description = fields.Text(translate=True)
    expression = fields.Text(required=True)
    field_dependencies = fields.Char()
    field_type = fields.Selection(
        [('float', 'Decimal'), ('integer', 'Integer'), ('boolean', 'Boolean')],
        default='float', required=True)
    active = fields.Boolean(default=True)
    company_id = fields.Many2one(
        'res.company', default=lambda self: self.env.company, required=True, index=True)

    def action_create_formula(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'New Formula Field',
            'res_model': 'rn.formula.field',
            'view_mode': 'form',
            'target': 'current',
            'context': {
                'default_name': self.name,
                'default_expression': self.expression,
                'default_field_dependencies': self.field_dependencies,
                'default_field_type': self.field_type,
            },
        }
