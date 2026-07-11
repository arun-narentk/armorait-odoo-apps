# -*- coding: utf-8 -*-

from datetime import date, timedelta

from odoo import api, fields, models, _
from odoo.tools import date_utils


class RnDomainDictionary(models.Model):
    _name = 'rn.domain.dictionary'
    _description = 'Domain Dictionary Entry'
    _order = 'res_model, sequence, trigger_word'

    name = fields.Char(required=True)
    res_model = fields.Selection(
        selection='_selection_res_model',
        string='Model',
        required=True,
        index=True,
    )
    trigger_word = fields.Char(
        required=True,
        help='Word or phrase matched in the user description.',
    )
    field_name = fields.Char(required=True)
    operator = fields.Selection(
        selection=[
            ('=', '='),
            ('!=', '!='),
            ('>', '>'),
            ('>=', '>='),
            ('<', '<'),
            ('<=', '<='),
            ('ilike', 'ilike'),
            ('in', 'in'),
        ],
        default='=',
        required=True,
    )
    value_type = fields.Selection(
        selection=[
            ('char', 'Text'),
            ('integer', 'Integer'),
            ('float', 'Float'),
            ('boolean', 'Boolean'),
            ('date_expression', 'Date Expression'),
        ],
        default='char',
        required=True,
    )
    value_char = fields.Char(string='Value')
    value_integer = fields.Integer(string='Integer Value')
    value_float = fields.Float(string='Float Value')
    value_boolean = fields.Boolean(string='Boolean Value')
    date_expression = fields.Selection(
        selection=[
            ('today', 'Today'),
            ('yesterday', 'Yesterday'),
            ('this_month', 'This Month'),
            ('last_month', 'Last Month'),
            ('this_week', 'This Week'),
            ('last_week', 'Last Week'),
            ('this_year', 'This Year'),
            ('next_month', 'Next Month'),
        ],
        string='Date Expression',
    )
    sequence = fields.Integer(default=10)
    active = fields.Boolean(default=True)
    company_id = fields.Many2one(
        'res.company',
        default=lambda self: self.env.company,
        index=True,
    )
    notes = fields.Text()

    @api.model
    def _selection_res_model(self):
        return self.env['rn.domain.parser.service'].supported_models()

    def get_resolved_value(self):
        self.ensure_one()
        if self.value_type == 'integer':
            return self.value_integer
        if self.value_type == 'float':
            return self.value_float
        if self.value_type == 'boolean':
            return self.value_boolean
        if self.value_type == 'date_expression':
            return self.date_expression or 'today'
        return self.value_char

    @api.model
    def resolve_date_expression(self, expression: str, today=None):
        today = today or date.today()
        if expression == 'today':
            return today.isoformat()
        if expression == 'yesterday':
            return (today - timedelta(days=1)).isoformat()
        if expression == 'this_week':
            start = today - timedelta(days=today.weekday())
            end = start + timedelta(days=6)
            return [start.isoformat(), end.isoformat()]
        if expression == 'last_week':
            end = today - timedelta(days=today.weekday() + 1)
            start = end - timedelta(days=6)
            return [start.isoformat(), end.isoformat()]
        if expression == 'this_month':
            start = today.replace(day=1)
            end = date_utils.end_of(today, 'month').date()
            return [start.isoformat(), end.isoformat()]
        if expression == 'last_month':
            first_this = today.replace(day=1)
            end = first_this - timedelta(days=1)
            start = end.replace(day=1)
            return [start.isoformat(), end.isoformat()]
        if expression == 'this_year':
            return [today.replace(month=1, day=1).isoformat(), today.replace(month=12, day=31).isoformat()]
        if expression == 'next_month':
            first_this = today.replace(day=1)
            if first_this.month == 12:
                start = first_this.replace(year=first_this.year + 1, month=1)
            else:
                start = first_this.replace(month=first_this.month + 1)
            end = date_utils.end_of(start, 'month').date()
            return [start.isoformat(), end.isoformat()]
        return today.isoformat()
