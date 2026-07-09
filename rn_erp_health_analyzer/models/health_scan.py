# -*- coding: utf-8 -*-
"""ERP health scan runs."""

from odoo import fields, models


class RnErpHealthScan(models.Model):
    _name = 'rn.erp.health.scan'
    _description = 'ERP Health Scan'
    _order = 'create_date desc'

    name = fields.Char(required=True, copy=False, default='New')
    target_id = fields.Many2one('rn.erp.health.target', required=True, ondelete='cascade', index=True)
    company_id = fields.Many2one(
        related='target_id.company_id',
        store=True,
        readonly=True,
    )
    state = fields.Selection(
        selection=[
            ('draft', 'Draft'),
            ('running', 'Running'),
            ('done', 'Done'),
            ('failed', 'Failed'),
        ],
        default='draft',
        required=True,
        index=True,
    )
    started_at = fields.Datetime()
    completed_at = fields.Datetime()
    overall_score = fields.Float(digits=(16, 2))
    risk_level = fields.Selection(
        selection=[
            ('low', 'Low'),
            ('medium', 'Medium'),
            ('high', 'High'),
            ('critical', 'Critical'),
        ],
        default='low',
        required=True,
    )
    summary = fields.Text()
    finding_ids = fields.One2many('rn.erp.health.finding', 'scan_id')
    finding_count = fields.Integer(compute='_compute_finding_count')
    high_risk_count = fields.Integer(compute='_compute_finding_count')

    def _compute_finding_count(self):
        for scan in self:
            scan.finding_count = len(scan.finding_ids)
            scan.high_risk_count = len(scan.finding_ids.filtered(lambda f: f.severity in ('high', 'critical')))
