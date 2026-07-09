# -*- coding: utf-8 -*-
"""Bottleneck and capacity constraint detection."""

import logging

from odoo import models

_logger = logging.getLogger(__name__)


class RnMrpBottleneckService(models.AbstractModel):
    """Identify slow work centers and waiting jobs."""

    _name = 'rn.mrp.bottleneck.service'
    _description = 'Bottleneck Service'

    def detect_bottlenecks(self, company_id=None):
        company_id = company_id or self.env.company.id
        bottlenecks = []
        statuses = self.env['rn.mrp.workcenter.status'].search([
            ('company_id', '=', company_id),
        ], order='queue_count desc')

        for status in statuses[:5]:
            if status.queue_count > 2 or status.status in ('breakdown', 'maintenance'):
                bottlenecks.append({
                    'workcenter': status.workcenter_id.name,
                    'status': status.status,
                    'queue': status.queue_count,
                    'utilization': status.utilization_percent,
                })

        slow_mos = self.env['mrp.production'].search([
            ('company_id', '=', company_id),
            ('state', '=', 'progress'),
        ], order='date_deadline asc', limit=5)
        at_risk = [
            {'mo': mo.name, 'product': mo.product_id.display_name, 'deadline': str(mo.date_deadline)}
            for mo in slow_mos if mo.date_deadline
        ]
        return {'workcenters': bottlenecks, 'orders_at_risk': at_risk}
