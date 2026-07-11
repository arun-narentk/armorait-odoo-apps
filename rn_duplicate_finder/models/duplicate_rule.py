# -*- coding: utf-8 -*-
"""Duplicate detection rules per Odoo model."""

from odoo import api, fields, models
from odoo.exceptions import ValidationError


class RnDupRule(models.Model):
    _name = 'rn.dup.rule'
    _description = 'Duplicate Detection Rule'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'sequence, name'

    name = fields.Char(required=True, tracking=True)
    active = fields.Boolean(default=True, tracking=True)
    sequence = fields.Integer(default=10)
    company_id = fields.Many2one(
        'res.company',
        default=lambda self: self.env.company,
        tracking=True,
    )
    model_id = fields.Many2one(
        'ir.model',
        string='Model',
        required=True,
        ondelete='cascade',
        domain=[('transient', '=', False)],
        tracking=True,
    )
    model_name = fields.Char(related='model_id.model', store=True, readonly=True)
    record_domain = fields.Char(
        string='Filter Domain',
        default='[]',
        help='Optional domain applied before scanning records.',
    )
    match_threshold = fields.Float(
        string='Match Threshold (%)',
        default=80.0,
        help='Minimum weighted score to flag a duplicate pair.',
    )
    batch_limit = fields.Integer(
        string='Record Limit',
        default=500,
        help='Maximum records loaded per scan for performance.',
    )
    auto_scan = fields.Boolean(
        string='Include in Scheduled Scan',
        default=False,
        tracking=True,
    )
    field_line_ids = fields.One2many(
        'rn.dup.rule.field',
        'rule_id',
        string='Matching Fields',
    )
    scan_ids = fields.One2many('rn.dup.scan', 'rule_id', string='Scans')
    scan_count = fields.Integer(compute='_compute_scan_count')
    last_scan_id = fields.Many2one('rn.dup.scan', compute='_compute_last_scan', store=True)
    last_match_count = fields.Integer(related='last_scan_id.match_count', readonly=True)

    @api.depends('scan_ids')
    def _compute_scan_count(self):
        grouped = self.env['rn.dup.scan'].read_group(
            [('rule_id', 'in', self.ids)],
            ['rule_id'],
            ['rule_id'],
        )
        counts = {row['rule_id'][0]: row['rule_id_count'] for row in grouped if row['rule_id']}
        for rule in self:
            rule.scan_count = counts.get(rule.id, 0)

    @api.depends('scan_ids.match_count', 'scan_ids.scan_date')
    def _compute_last_scan(self):
        for rule in self:
            last = self.env['rn.dup.scan'].search(
                [('rule_id', '=', rule.id)],
                order='scan_date desc, id desc',
                limit=1,
            )
            rule.last_scan_id = last.id if last else False

    @api.constrains('field_line_ids', 'match_threshold')
    def _check_rule_config(self):
        for rule in self:
            if self.env.context.get('install_mode') or self.env.context.get('module'):
                continue
            if not rule.field_line_ids:
                raise ValidationError('Add at least one matching field on the rule.')
            total_weight = sum(rule.field_line_ids.mapped('weight'))
            if total_weight <= 0:
                raise ValidationError('Total field weight must be greater than zero.')
            if rule.match_threshold <= 0 or rule.match_threshold > 100:
                raise ValidationError('Match threshold must be between 1 and 100.')

    @api.constrains('record_domain')
    def _check_record_domain(self):
        for rule in self:
            try:
                domain = rule._get_record_domain()
            except Exception as exc:
                raise ValidationError(f'Invalid filter domain: {exc}') from exc
            if not isinstance(domain, list):
                raise ValidationError('Filter domain must evaluate to a list.')

    def _get_record_domain(self):
        self.ensure_one()
        domain = []
        if self.record_domain:
            domain = eval(self.record_domain, {'uid': self.env.uid})  # noqa: S307
        if self.model_name in self.env and 'company_id' in self.env[self.model_name]._fields:
            domain = list(domain) + [('company_id', 'in', [False, self.company_id.id])]
        return domain

    def action_run_scan(self):
        self.ensure_one()
        scan = self.env['rn.dup.scan.service'].run_rule_scan(self)
        return {
            'type': 'ir.actions.act_window',
            'name': 'Duplicate Scan',
            'res_model': 'rn.dup.scan',
            'view_mode': 'form',
            'res_id': scan.id,
        }
