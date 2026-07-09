# -*- coding: utf-8 -*-
"""Company workflow settings."""

from odoo import fields, models


class RnWorkflowSettings(models.Model):
    """Per-company automation platform settings."""

    _name = 'rn.workflow.settings'
    _description = 'Workflow Settings'
    _rec_name = 'company_id'

    company_id = fields.Many2one('res.company', required=True, ondelete='cascade', index=True)
    max_active_workflows = fields.Integer(string='Max Active Workflows', default=25)
    allow_python_actions = fields.Boolean(string='Allow Python Actions', default=False)
    allow_external_webhooks = fields.Boolean(string='Allow External Webhooks', default=True)
    ai_builder_enabled = fields.Boolean(string='AI Workflow Builder', default=True)
    retry_failed_runs = fields.Boolean(string='Auto Retry Failed Runs', default=True)
    max_retry_count = fields.Integer(default=3)
    execution_log_days = fields.Integer(string='Keep Logs (days)', default=90)
    webhook_secret = fields.Char(copy=False)
    _sql_constraints = [
        ('company_uniq', 'unique(company_id)', 'Only one workflow settings record per company.'),
    ]
