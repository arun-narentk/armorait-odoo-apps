# -*- coding: utf-8 -*-
"""Production, WIP, and inventory KPI calculations."""

import logging
from datetime import timedelta

from odoo import fields, models

_logger = logging.getLogger(__name__)


class RnMrpKpiService(models.AbstractModel):
    """Calculate manufacturing KPIs from Odoo MRP and stock data."""

    _name = 'rn.mrp.kpi.service'
    _description = 'Manufacturing KPI Service'

    def get_executive_summary(self, company_id=None):
        company_id = company_id or self.env.company.id
        today = fields.Date.context_today(self)
        Production = self.env['mrp.production']
        base_domain = [('company_id', '=', company_id)]

        today_domain = base_domain + [
            ('date_start', '>=', today),
            ('date_start', '<', today + timedelta(days=1)),
        ]
        mos_today = Production.search(today_domain)
        all_open = Production.search(base_domain + [('state', 'in', ('confirmed', 'progress'))])

        planned_qty = sum(mos_today.mapped('product_qty'))
        produced_qty = sum(
            mo.qty_produced for mo in mos_today if mo.state in ('done', 'progress')
        )
        completed = Production.search_count(base_domain + [
            ('state', '=', 'done'),
            ('date_finished', '>=', today),
            ('date_finished', '<', today + timedelta(days=1)),
        ])
        delayed = Production.search_count(base_domain + [
            ('state', 'in', ('confirmed', 'progress')),
            ('date_deadline', '<', today),
        ])

        wc_status = self.env['rn.mrp.workcenter.status'].search([
            ('company_id', '=', company_id),
        ])
        running = len(wc_status.filtered(lambda s: s.status == 'running'))
        total_wc = len(wc_status) or 1
        utilization = round(running / total_wc * 100, 1)

        wip_value = self._estimate_wip_value(company_id)
        scrap_qty = sum(mo.scrap_ids.mapped('scrap_qty') for mo in mos_today if hasattr(mo, 'scrap_ids'))

        return {
            'today_production_pct': round(produced_qty / planned_qty * 100, 1) if planned_qty else 0.0,
            'orders_completed': completed,
            'orders_delayed': delayed,
            'machine_utilization': utilization,
            'wip_orders': len(all_open),
            'wip_value': wip_value,
            'scrap_qty': scrap_qty,
            'planned_qty': planned_qty,
            'produced_qty': produced_qty,
        }

    def get_production_output(self, company_id=None):
        company_id = company_id or self.env.company.id
        today = fields.Date.context_today(self)
        Production = self.env['mrp.production']
        base = [('company_id', '=', company_id), ('state', '=', 'done')]

        def qty_since(days):
            start = today - timedelta(days=days)
            mos = Production.search(base + [('date_finished', '>=', start)])
            return sum(mos.mapped('qty_produced'))

        return {
            'today': qty_since(0),
            'week': qty_since(7),
            'month': qty_since(30),
        }

    def get_inventory_risks(self, company_id=None):
        company_id = company_id or self.env.company.id
        settings = self.env['rn.mrp.intelligence.settings'].search(
            [('company_id', '=', company_id)], limit=1,
        )
        days = settings.low_stock_days if settings else 3
        products = self.env['product.product'].search([
            ('type', 'in', ('product', 'consu')),
        ], limit=200)
        low_stock = 0
        for product in products:
            qty = product.with_company(company_id).qty_available
            if qty < 1:
                low_stock += 1
        pending_po = self.env['purchase.order'].search_count([
            ('company_id', '=', company_id),
            ('state', 'in', ('purchase', 'sent')),
        ])
        late_po = self.env['purchase.order'].search_count([
            ('company_id', '=', company_id),
            ('state', 'in', ('purchase', 'sent')),
            ('date_planned', '<', fields.Datetime.now()),
        ])
        return {
            'low_stock_items': low_stock,
            'pending_purchase_orders': pending_po,
            'late_purchase_orders': late_po,
            'low_stock_days_threshold': days,
        }

    def _estimate_wip_value(self, company_id):
        mos = self.env['mrp.production'].search([
            ('company_id', '=', company_id),
            ('state', 'in', ('confirmed', 'progress')),
        ], limit=50)
        total = 0.0
        for mo in mos:
            price = mo.product_id.standard_price or 0.0
            total += price * (mo.product_qty - mo.qty_produced)
        return round(total, 2)
