# -*- coding: utf-8 -*-

import re

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

from ..services.formula_engine import FormulaEngine


class FormulaField(models.Model):
    _name = 'rn.formula.field'
    _description = 'Formula Field'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'model_name, field_name'

    name = fields.Char(required=True, tracking=True)
    model_id = fields.Many2one('ir.model', required=True, ondelete='cascade', tracking=True)
    model_name = fields.Char(related='model_id.model', store=True, readonly=True, index=True)
    field_name = fields.Char(required=True, index=True, tracking=True)
    expression = fields.Text(required=True, tracking=True)
    field_dependencies = fields.Char(
        help="Comma-separated model field names used by this expression.")
    field_type = fields.Selection(
        [('float', 'Decimal'), ('integer', 'Integer'), ('boolean', 'Boolean')],
        default='float', required=True)
    active = fields.Boolean(default=True, tracking=True)
    company_id = fields.Many2one(
        'res.company', default=lambda self: self.env.company, required=True, index=True)
    ir_field_id = fields.Many2one('ir.model.fields', readonly=True, ondelete='set null')
    _engine = FormulaEngine()

    _sql_constraints = [
        ('formula_field_model_unique', 'unique(model_id, field_name)',
         'Only one formula may use a field name on a model.'),
    ]

    @api.constrains('field_name')
    def _check_field_name(self):
        for record in self:
            if not re.fullmatch(r'x_rn_formula_[a-z0-9_]+', record.field_name or ''):
                raise ValidationError(_(
                    "Formula field names must start with 'x_rn_formula_' and use lowercase letters, numbers, or underscores."))

    @api.constrains('expression', 'field_dependencies', 'model_id')
    def _check_expression(self):
        for record in self:
            record._engine.validate(record.expression)
            dependencies = record._dependency_names()
            invalid = set(dependencies) - set(record.model_id.field_id.mapped('name'))
            if invalid:
                raise ValidationError(_("Unknown model fields: %s") % ', '.join(sorted(invalid)))
            if record.field_name in dependencies:
                raise ValidationError(_("A formula cannot depend on itself."))

    def _dependency_names(self):
        self.ensure_one()
        if self.field_dependencies:
            return [name.strip() for name in self.field_dependencies.split(',') if name.strip()]
        return self._engine._extract_names(self.expression)

    def _compute_code(self):
        self.ensure_one()
        return """formula = self.env['rn.formula.field'].search([('field_name', '=', '%(field)s'), ('model_name', '=', '%(model)s'), ('active', '=', True)], limit=1)
for record in self:
    if formula:
        record['%(field)s'] = formula._engine.evaluate_record(formula, record)
    else:
        record['%(field)s'] = False""" % {
            'field': self.field_name.replace("'", "\\'"),
            'model': self.model_name.replace("'", "\\'"),
        }

    def _sync_ir_field(self):
        """Create or update the dynamic computed field used by the formula."""
        IrFields = self.env['ir.model.fields'].sudo()
        for formula in self:
            values = {
                'name': formula.field_name,
                'field_description': formula.name,
                'model_id': formula.model_id.id,
                'ttype': formula.field_type,
                'state': 'manual',
                'compute': formula._compute_code(),
                'store': True,
                'readonly': True,
                'depends': ','.join(formula._dependency_names()),
            }
            ir_field = formula.ir_field_id.exists() or IrFields.search([
                ('model_id', '=', formula.model_id.id), ('name', '=', formula.field_name),
            ], limit=1)
            if ir_field:
                ir_field.write(values)
            else:
                ir_field = IrFields.create(values)
            formula.ir_field_id = ir_field.id

    @api.model_create_multi
    def create(self, values_list):
        records = super().create(values_list)
        records._sync_ir_field()
        return records

    def write(self, values):
        result = super().write(values)
        if {'name', 'model_id', 'field_name', 'expression', 'field_dependencies',
                'field_type', 'active'} & set(values):
            self._sync_ir_field()
        return result

    def action_open_test_wizard(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Test Formula'),
            'res_model': 'rn.formula.test.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_formula_id': self.id},
        }
