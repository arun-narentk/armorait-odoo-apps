# -*- coding: utf-8 -*-
"""Ignored duplicate pairs."""

from odoo import api, fields, models


class RnDupIgnore(models.Model):
    _name = 'rn.dup.ignore'
    _description = 'Ignored Duplicate Pair'
    _order = 'id desc'

    rule_id = fields.Many2one('rn.dup.rule', required=True, ondelete='cascade', index=True)
    company_id = fields.Many2one(
        'res.company',
        related='rule_id.company_id',
        store=True,
        readonly=True,
    )
    model_name = fields.Char(required=True, index=True)
    res_id = fields.Integer(required=True, index=True)
    duplicate_res_id = fields.Integer(required=True, index=True)
    note = fields.Char()

    _sql_constraints = [
        (
            'uniq_ignore_pair',
            'unique(rule_id, model_name, res_id, duplicate_res_id)',
            'This pair is already ignored for the rule.',
        ),
    ]

    @api.model
    def _pair_key(self, res_id, duplicate_res_id):
        low, high = sorted((res_id, duplicate_res_id))
        return low, high

    @api.model
    def _register_ignore(self, rule, model_name, res_id, duplicate_res_id, note=None):
        low, high = self._pair_key(res_id, duplicate_res_id)
        existing = self.search([
            ('rule_id', '=', rule.id),
            ('model_name', '=', model_name),
            ('res_id', '=', low),
            ('duplicate_res_id', '=', high),
        ], limit=1)
        if existing:
            return existing
        return self.create({
            'rule_id': rule.id,
            'model_name': model_name,
            'res_id': low,
            'duplicate_res_id': high,
            'note': note,
        })

    @api.model
    def is_ignored(self, rule, model_name, res_id, duplicate_res_id):
        low, high = self._pair_key(res_id, duplicate_res_id)
        return bool(self.search_count([
            ('rule_id', '=', rule.id),
            ('model_name', '=', model_name),
            ('res_id', '=', low),
            ('duplicate_res_id', '=', high),
        ]))
