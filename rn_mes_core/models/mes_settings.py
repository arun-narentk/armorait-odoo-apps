# -*- coding: utf-8 -*-
"""Company-level MES configuration."""

from odoo import fields, models


class RnMesSettings(models.Model):
    """Per-company MES defaults and feature toggles."""

    _name = 'rn.mes.settings'
    _description = 'MES Settings'
    _rec_name = 'company_id'

    company_id = fields.Many2one('res.company', required=True, ondelete='cascade', index=True)
    auto_oee_snapshot = fields.Boolean(
        string='Daily OEE Snapshot',
        default=True,
        help='Compute OEE snapshots from downtime and production events.',
    )
    require_quality_on_complete = fields.Boolean(
        string='Quality Check Before Complete',
        default=False,
    )
    default_checklist_id = fields.Many2one('rn.mes.quality.checklist', string='Default Checklist')
    tablet_pin_required = fields.Boolean(string='Operator PIN on Tablet', default=False)
    iot_gateway_url = fields.Char(string='IoT Gateway Base URL')
    ai_insights_enabled = fields.Boolean(string='AI Production Insights', default=True)
    _sql_constraints = [
        ('company_uniq', 'unique(company_id)', 'Only one MES settings record per company.'),
    ]
