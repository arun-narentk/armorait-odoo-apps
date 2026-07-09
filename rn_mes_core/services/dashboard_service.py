# -*- coding: utf-8 -*-
"""Plant manager dashboard payload."""

import logging

from odoo import fields, models

_logger = logging.getLogger(__name__)


class RnMesDashboardService(models.AbstractModel):
    """Aggregate live MES KPIs for OWL dashboard."""

    _name = 'rn.mes.dashboard.service'
    _description = 'MES Dashboard Service'

    def get_dashboard_data(self, company_id=None):
        company_id = company_id or self.env.company.id
        today = fields.Date.context_today(self)
        Session = self.env['rn.mes.production.session']
        Downtime = self.env['rn.mes.downtime.event']
        Oee = self.env['rn.mes.oee.snapshot']
        Device = self.env['rn.mes.machine.device']

        active_sessions = Session.search([
            ('company_id', '=', company_id),
            ('state', 'in', ('active', 'paused')),
        ])
        open_downtime = Downtime.search_count([
            ('company_id', '=', company_id),
            ('state', '=', 'open'),
        ])
        oee_records = Oee.search([
            ('company_id', '=', company_id),
            ('snapshot_date', '=', today),
        ])
        avg_oee = (
            round(sum(oee_records.mapped('oee')) / len(oee_records), 1)
            if oee_records else 0.0
        )
        devices = Device.search([('company_id', '=', company_id), ('active', '=', True)])
        insight = self.env['rn.mes.insight.service'].analyze_line_performance(company_id=company_id)

        return {
            'active_sessions': len(active_sessions),
            'paused_sessions': len(active_sessions.filtered(lambda s: s.state == 'paused')),
            'open_downtime': open_downtime,
            'machines': {
                'running': len(devices.filtered(lambda d: d.status == 'running')),
                'idle': len(devices.filtered(lambda d: d.status == 'idle')),
                'alarm': len(devices.filtered(lambda d: d.status == 'alarm')),
                'offline': len(devices.filtered(lambda d: d.status == 'offline')),
            },
            'oee_avg': avg_oee,
            'good_qty_today': insight.get('good_qty', 0.0),
            'scrap_qty_today': insight.get('scrap_qty', 0.0),
            'ai_summary': insight.get('summary', ''),
            'updated_at': fields.Datetime.to_string(fields.Datetime.now()),
        }
