# -*- coding: utf-8 -*-
"""Manufacturing intelligence dashboard payload."""

import logging

from odoo import fields, models

_logger = logging.getLogger(__name__)


class RnMrpDashboardService(models.AbstractModel):
    """Aggregate dashboard data for OWL client."""

    _name = 'rn.mrp.dashboard.service'
    _description = 'Manufacturing Dashboard Service'

    def get_dashboard_data(self, company_id=None):
        company_id = company_id or self.env.company.id
        Kpi = self.env['rn.mrp.kpi.service']
        executive = Kpi.get_executive_summary(company_id)
        production = Kpi.get_production_output(company_id)
        inventory = Kpi.get_inventory_risks(company_id)
        bottlenecks = self.env['rn.mrp.bottleneck.service'].detect_bottlenecks(company_id)

        wc_status = self.env['rn.mrp.workcenter.status'].search([
            ('company_id', '=', company_id),
        ])
        oee_records = self.env['rn.mrp.oee.record'].search([
            ('company_id', '=', company_id),
            ('date', '=', fields.Date.context_today(self)),
        ], limit=10)
        avg_oee = (
            round(sum(oee_records.mapped('oee')) / len(oee_records), 1)
            if oee_records else 0.0
        )

        latest_insight = self.env['rn.mrp.ai.insight'].search([
            ('company_id', '=', company_id),
            ('insight_type', '=', 'daily_summary'),
        ], limit=1)

        return {
            'executive': executive,
            'production': production,
            'inventory': inventory,
            'workcenters': {
                'running': len(wc_status.filtered(lambda s: s.status == 'running')),
                'idle': len(wc_status.filtered(lambda s: s.status == 'idle')),
                'breakdown': len(wc_status.filtered(lambda s: s.status == 'breakdown')),
                'maintenance': len(wc_status.filtered(lambda s: s.status == 'maintenance')),
                'offline': len(wc_status.filtered(lambda s: s.status == 'offline')),
            },
            'oee_avg': avg_oee,
            'bottlenecks': bottlenecks,
            'ai_summary': latest_insight.summary_html if latest_insight else '',
            'updated_at': fields.Datetime.to_string(fields.Datetime.now()),
        }
