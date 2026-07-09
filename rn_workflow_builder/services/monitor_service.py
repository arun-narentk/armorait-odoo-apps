# -*- coding: utf-8 -*-
"""Monitoring dashboard data."""

from dateutil.relativedelta import relativedelta

from odoo import fields, models


class RnWorkflowMonitorService(models.AbstractModel):
    """Operational metrics for workflow platform."""

    _name = 'rn.workflow.monitor.service'
    _description = 'Workflow Monitor Service'

    def get_dashboard_data(self, company_id=None):
        company_id = company_id or self.env.company.id
        Workflow = self.env['rn.workflow']
        Run = self.env['rn.workflow.run']

        workflows = Workflow.search([('company_id', '=', company_id)])
        active = workflows.filtered(lambda w: w.state == 'active')
        week_ago = fields.Datetime.now() - relativedelta(days=7)
        runs = Run.search([
            ('company_id', '=', company_id),
            ('start_time', '>=', week_ago),
        ])
        done = runs.filtered(lambda r: r.state == 'done')
        failed = runs.filtered(lambda r: r.state == 'failed')
        retry = runs.filtered(lambda r: r.state == 'retry')
        avg_ms = (
            round(sum(done.mapped('duration_ms')) / len(done), 0)
            if done else 0
        )
        success_rate = round((len(done) / len(runs)) * 100.0, 1) if runs else 0.0

        return {
            'total_workflows': len(workflows),
            'active_workflows': len(active),
            'runs_7d': len(runs),
            'failed_runs': len(failed),
            'retry_queue': len(retry),
            'success_rate': success_rate,
            'avg_duration_ms': avg_ms,
            'suggestions': self.env['rn.workflow.ai.service'].suggest_automations(company_id),
            'updated_at': fields.Datetime.to_string(fields.Datetime.now()),
        }
