# -*- coding: utf-8 -*-
"""Detailed ERP health findings."""

from odoo import fields, models


class RnErpHealthFinding(models.Model):
    _name = 'rn.erp.health.finding'
    _description = 'ERP Health Finding'
    _order = 'severity desc, create_date desc'

    name = fields.Char(required=True)
    scan_id = fields.Many2one('rn.erp.health.scan', required=True, ondelete='cascade', index=True)
    target_id = fields.Many2one(related='scan_id.target_id', store=True, readonly=True)
    company_id = fields.Many2one(related='scan_id.company_id', store=True, readonly=True)
    code = fields.Char(required=True, index=True)
    category = fields.Selection(
        selection=[
            ('performance', 'Performance'),
            ('security', 'Security'),
            ('data_quality', 'Data Quality'),
            ('accounting', 'Accounting'),
            ('modules', 'Modules'),
            ('operations', 'Operations'),
            ('upgrade', 'Upgrade Readiness'),
        ],
        required=True,
        index=True,
    )
    severity = fields.Selection(
        selection=[
            ('info', 'Info'),
            ('low', 'Low'),
            ('medium', 'Medium'),
            ('high', 'High'),
            ('critical', 'Critical'),
        ],
        default='low',
        required=True,
        index=True,
    )
    state = fields.Selection(
        selection=[
            ('open', 'Open'),
            ('resolved', 'Resolved'),
            ('ignored', 'Ignored'),
        ],
        default='open',
        required=True,
        index=True,
    )
    score_impact = fields.Integer(default=0)
    model_name = fields.Char()
    metric_value = fields.Float(digits=(16, 2))
    recommendation = fields.Text(required=True)
    technical_details = fields.Text()
