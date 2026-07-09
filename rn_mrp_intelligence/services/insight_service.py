# -*- coding: utf-8 -*-
"""AI-style factory summary generation."""

import logging

from odoo import fields, models

_logger = logging.getLogger(__name__)


class RnMrpInsightService(models.AbstractModel):
    """Build narrative factory summaries from KPI data."""

    _name = 'rn.mrp.insight.service'
    _description = 'Manufacturing Insight Service'

    def generate_daily_summary(self, company_id=None):
        company_id = company_id or self.env.company.id
        kpi = self.env['rn.mrp.kpi.service'].get_executive_summary(company_id)
        bottlenecks = self.env['rn.mrp.bottleneck.service'].detect_bottlenecks(company_id)
        inventory = self.env['rn.mrp.kpi.service'].get_inventory_risks(company_id)

        lines = []
        pct = kpi['today_production_pct']
        lines.append(
            f'Production today reached {pct}% of plan '
            f'({kpi["produced_qty"]:.0f} of {kpi["planned_qty"]:.0f} units).'
        )
        if kpi['orders_delayed']:
            lines.append(f'{kpi["orders_delayed"]} manufacturing orders are past deadline.')
        if bottlenecks['workcenters']:
            wc = bottlenecks['workcenters'][0]
            lines.append(
                f'Work center "{wc["workcenter"]}" shows {wc["status"]} status '
                f'with queue length {wc["queue"]}.'
            )
        if inventory['low_stock_items']:
            lines.append(
                f'{inventory["low_stock_items"]} materials are at or below reorder levels.'
            )
        if inventory['late_purchase_orders']:
            lines.append(f'{inventory["late_purchase_orders"]} purchase orders are late.')

        summary = ' '.join(lines)
        html = f'<p>{summary}</p>'
        insight = self.env['rn.mrp.ai.insight'].create({
            'name': f'Daily Summary {fields.Date.context_today(self)}',
            'insight_type': 'daily_summary',
            'summary_html': html,
            'severity': 'warning' if kpi['orders_delayed'] else 'info',
            'company_id': company_id,
        })
        return insight
