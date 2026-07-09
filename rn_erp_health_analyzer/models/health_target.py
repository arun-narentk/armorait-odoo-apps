# -*- coding: utf-8 -*-
"""Scan targets for ERP intelligence analysis."""

from odoo import fields, models


class RnErpHealthTarget(models.Model):
    _name = 'rn.erp.health.target'
    _description = 'ERP Health Target'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'name'

    name = fields.Char(required=True, tracking=True)
    active = fields.Boolean(default=True)
    company_id = fields.Many2one(
        'res.company',
        required=True,
        default=lambda self: self.env.company,
        tracking=True,
    )
    target_type = fields.Selection(
        selection=[
            ('database', 'Database'),
            ('operations', 'Operations'),
            ('finance', 'Finance'),
            ('security', 'Security'),
            ('upgrade', 'Upgrade Readiness'),
        ],
        default='database',
        required=True,
        tracking=True,
    )
    scope_note = fields.Text(help='Optional scope notes or customer context.')
    last_scan_id = fields.Many2one('rn.erp.health.scan', readonly=True, copy=False)
    last_score = fields.Float(readonly=True, digits=(16, 2))
    finding_open_count = fields.Integer(compute='_compute_finding_counts')
    scan_count = fields.Integer(compute='_compute_finding_counts')

    def _compute_finding_counts(self):
        scan_data = self.env['rn.erp.health.scan'].read_group(
            [('target_id', 'in', self.ids)], ['target_id'], ['target_id']
        )
        scan_map = {item['target_id'][0]: item['target_id_count'] for item in scan_data if item['target_id']}
        open_data = self.env['rn.erp.health.finding'].read_group(
            [('target_id', 'in', self.ids), ('state', '=', 'open')], ['target_id'], ['target_id']
        )
        open_map = {item['target_id'][0]: item['target_id_count'] for item in open_data if item['target_id']}
        for target in self:
            target.scan_count = scan_map.get(target.id, 0)
            target.finding_open_count = open_map.get(target.id, 0)

    def action_run_scan(self):
        for target in self:
            self.env['rn.erp.health.scan.service'].run_scan(target)
        return True
