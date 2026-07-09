# -*- coding: utf-8 -*-
"""OEE calculation from downtime and production data."""

import logging

from odoo import fields, models

_logger = logging.getLogger(__name__)


class RnMesOeeService(models.AbstractModel):
    """Compute and store OEE snapshots."""

    _name = 'rn.mes.oee.service'
    _description = 'MES OEE Service'

    def compute_snapshot(self, workcenter_id, snapshot_date=None, shift_label=''):
        workcenter = self.env['mrp.workcenter'].browse(workcenter_id)
        if not workcenter.exists():
            return False
        snapshot_date = snapshot_date or fields.Date.context_today(self)
        planned = float(workcenter.time_efficiency or 100.0) * 8.0 * 60.0 / 100.0
        planned = planned or 480.0

        downtime_events = self.env['rn.mes.downtime.event'].search([
            ('workcenter_id', '=', workcenter.id),
            ('start_time', '>=', fields.Datetime.to_datetime(snapshot_date)),
            ('company_id', '=', workcenter.company_id.id),
        ])
        downtime_minutes = sum(downtime_events.mapped('duration_minutes'))
        running_minutes = max(planned - downtime_minutes, 0.0)
        availability = round((running_minutes / planned) * 100.0, 2) if planned else 0.0

        sessions = self.env['rn.mes.production.session'].search([
            ('workcenter_id', '=', workcenter.id),
            ('start_time', '>=', fields.Datetime.to_datetime(snapshot_date)),
            ('company_id', '=', workcenter.company_id.id),
        ])
        good_qty = sum(sessions.mapped('good_qty'))
        scrap_qty = sum(sessions.mapped('scrap_qty'))
        reject_qty = sum(sessions.mapped('reject_qty'))
        total_qty = good_qty + scrap_qty + reject_qty
        quality = round((good_qty / total_qty) * 100.0, 2) if total_qty else 100.0

        expected_rate = 1.0
        actual_rate = (good_qty / running_minutes) if running_minutes else 0.0
        performance = round(min((actual_rate / expected_rate) * 100.0, 100.0), 2) if expected_rate else 100.0

        name = f'{workcenter.name} OEE {snapshot_date}'
        return self.env['rn.mes.oee.snapshot'].create({
            'name': name,
            'workcenter_id': workcenter.id,
            'snapshot_date': snapshot_date,
            'shift_label': shift_label,
            'availability': availability,
            'performance': performance,
            'quality': quality,
            'planned_minutes': planned,
            'running_minutes': running_minutes,
            'downtime_minutes': downtime_minutes,
            'good_qty': good_qty,
            'total_qty': total_qty,
            'company_id': workcenter.company_id.id,
        })

    def run_daily_snapshots(self, company_id=None):
        company_id = company_id or self.env.company.id
        workcenters = self.env['mrp.workcenter'].search([('company_id', '=', company_id)])
        created = self.env['rn.mes.oee.snapshot']
        for wc in workcenters:
            created |= self.compute_snapshot(wc.id)
        return created.ids
