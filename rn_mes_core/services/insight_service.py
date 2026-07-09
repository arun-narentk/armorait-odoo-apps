# -*- coding: utf-8 -*-
"""Heuristic production insights (AI-ready)."""

import logging

from odoo import fields, models

_logger = logging.getLogger(__name__)


class RnMesInsightService(models.AbstractModel):
    """Explain production misses using downtime, quality, and alarms."""

    _name = 'rn.mes.insight.service'
    _description = 'MES Insight Service'

    def analyze_line_performance(self, workcenter_id=None, company_id=None):
        company_id = company_id or self.env.company.id
        domain = [('company_id', '=', company_id), ('state', '=', 'closed')]
        if workcenter_id:
            domain.append(('workcenter_id', '=', workcenter_id))
        today = fields.Date.context_today(self)
        downtime = self.env['rn.mes.downtime.event'].search(
            domain + [('start_time', '>=', fields.Datetime.to_datetime(today))],
        )
        sessions = self.env['rn.mes.production.session'].search([
            ('company_id', '=', company_id),
            ('start_time', '>=', fields.Datetime.to_datetime(today)),
        ])
        alarms = self.env['rn.mes.machine.device'].search([
            ('company_id', '=', company_id),
            ('status', '=', 'alarm'),
        ])

        downtime_by_reason = {}
        for evt in downtime:
            reason = evt.reason_id.name or 'Unknown'
            downtime_by_reason[reason] = downtime_by_reason.get(reason, 0.0) + evt.duration_minutes

        scrap_total = sum(sessions.mapped('scrap_qty')) + sum(sessions.mapped('reject_qty'))
        good_total = sum(sessions.mapped('good_qty'))

        bullets = []
        if downtime_by_reason:
            top = max(downtime_by_reason.items(), key=lambda x: x[1])
            bullets.append(
                f'Top downtime driver: {top[0]} ({round(top[1], 1)} minutes).'
            )
        if scrap_total:
            bullets.append(
                f'Scrap/reject quantity today: {scrap_total} units vs {good_total} good.'
            )
        if alarms:
            bullets.append(
                f'{len(alarms)} machine(s) in alarm state.'
            )
        if not bullets:
            bullets.append('No major shop-floor issues detected for today.')

        return {
            'summary': ' '.join(bullets),
            'downtime_minutes': sum(downtime.mapped('duration_minutes')),
            'good_qty': good_total,
            'scrap_qty': scrap_total,
            'alarm_count': len(alarms),
            'generated_at': fields.Datetime.to_string(fields.Datetime.now()),
        }
