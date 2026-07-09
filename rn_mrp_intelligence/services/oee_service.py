# -*- coding: utf-8 -*-
"""OEE calculation service."""

import logging
from datetime import timedelta

from odoo import fields, models

_logger = logging.getLogger(__name__)


class RnMrpOeeService(models.AbstractModel):
    """Compute OEE metrics for work centers."""

    _name = 'rn.mrp.oee.service'
    _description = 'OEE Service'

    def compute_workcenter_oee(self, workcenter, date=None, company_id=None):
        company_id = company_id or self.env.company.id
        date = date or fields.Date.context_today(self)
        day_start = fields.Datetime.to_datetime(date)
        day_end = day_start + timedelta(days=1)

        downtime = self.env['rn.mrp.downtime.log'].search([
            ('workcenter_id', '=', workcenter.id),
            ('company_id', '=', company_id),
            ('date_start', '>=', day_start),
            ('date_start', '<', day_end),
        ])
        downtime_min = sum(downtime.mapped('duration_minutes'))
        planned_min = 480.0
        running_min = max(planned_min - downtime_min, 0.0)
        availability = round(running_min / planned_min * 100, 1) if planned_min else 0.0

        mos = self.env['mrp.production'].search([
            ('company_id', '=', company_id),
            ('workorder_ids.workcenter_id', '=', workcenter.id),
            ('date_start', '>=', day_start),
            ('date_start', '<', day_end),
        ])
        good_qty = sum(mos.mapped('qty_produced'))
        planned_qty = sum(mos.mapped('product_qty')) or 1.0
        performance = round(min(good_qty / planned_qty * 100, 100), 1)
        quality = 98.0
        if hasattr(mos, 'scrap_ids'):
            scrap = sum(mo.scrap_ids.mapped('scrap_qty') for mo in mos)
            total = good_qty + scrap
            if total:
                quality = round(good_qty / total * 100, 1)

        return {
            'availability': availability,
            'performance': performance,
            'quality': quality,
            'oee': round(availability * performance * quality / 10000.0, 2),
            'downtime_minutes': downtime_min,
            'running_minutes': running_min,
            'good_qty': good_qty,
            'total_qty': planned_qty,
        }

    def refresh_oee_records(self, company_id=None):
        company_id = company_id or self.env.company.id
        today = fields.Date.context_today(self)
        Oee = self.env['rn.mrp.oee.record']
        for wc in self.env['mrp.workcenter'].search([('company_id', '=', company_id)]):
            metrics = self.compute_workcenter_oee(wc, today, company_id)
            existing = Oee.search([
                ('workcenter_id', '=', wc.id),
                ('date', '=', today),
                ('company_id', '=', company_id),
            ], limit=1)
            vals = {
                'name': f'OEE {wc.name} {today}',
                'workcenter_id': wc.id,
                'date': today,
                'availability': metrics['availability'],
                'performance': metrics['performance'],
                'quality': metrics['quality'],
                'planned_minutes': 480,
                'running_minutes': metrics['running_minutes'],
                'downtime_minutes': metrics['downtime_minutes'],
                'good_qty': metrics['good_qty'],
                'total_qty': metrics['total_qty'],
                'company_id': company_id,
            }
            if existing:
                existing.write(vals)
            else:
                Oee.create(vals)
