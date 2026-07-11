# -*- coding: utf-8 -*-
"""Weighted field lines on duplicate rules."""

from odoo import api, fields, models
from odoo.exceptions import ValidationError


class RnDupRuleField(models.Model):
    _name = 'rn.dup.rule.field'
    _description = 'Duplicate Rule Field'
    _order = 'sequence, id'

    rule_id = fields.Many2one('rn.dup.rule', required=True, ondelete='cascade')
    sequence = fields.Integer(default=10)
    field_name = fields.Char(required=True, string='Field Technical Name')
    label = fields.Char(compute='_compute_label', store=True)
    match_type = fields.Selection(
        selection=[
            ('exact', 'Exact'),
            ('fuzzy', 'Fuzzy'),
            ('phone', 'Phone Digits'),
        ],
        default='fuzzy',
        required=True,
    )
    weight = fields.Float(default=50.0, required=True)

    def _compute_label(self):
        for line in self:
            label = line.field_name or ''
            rule = line.rule_id
            if rule.model_name and line.field_name and line.field_name in rule.env[rule.model_name]._fields:
                label = rule.env[rule.model_name]._fields[line.field_name].string
            line.label = label

    @api.constrains('weight')
    def _check_weight(self):
        for line in self:
            if line.weight <= 0:
                raise ValidationError('Field weight must be greater than zero.')
