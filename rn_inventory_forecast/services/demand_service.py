# -*- coding: utf-8 -*-
"""Historical demand aggregation from sales and stock moves."""

import logging
from collections import defaultdict
from datetime import timedelta

from odoo import fields, models

_logger = logging.getLogger(__name__)


class RnInvDemandService(models.AbstractModel):
    """Collect historical demand by product."""

    _name = 'rn.inv.demand.service'
    _description = 'Inventory Demand Service'

    def get_history_window(self, company_id=None, history_days=None):
        """Return (date_from, date_to) for demand history."""
        company_id = company_id or self.env.company.id
        settings = self.env['rn.inv.forecast.settings'].search(
            [('company_id', '=', company_id)], limit=1
        )
        days = history_days or (settings.history_days if settings else 90)
        today = fields.Date.context_today(self)
        return today - timedelta(days=max(1, days) - 1), today

    def demand_by_product(self, date_from, date_to, company_id=None, warehouse_id=None):
        """Aggregate outgoing stock quantity per product in range."""
        company_id = company_id or self.env.company.id
        domain = [
            ('state', '=', 'done'),
            ('date', '>=', fields.Datetime.to_string(fields.Datetime.to_datetime(date_from))),
            ('date', '<=', fields.Datetime.to_string(fields.Datetime.to_datetime(date_to))[:10] + ' 23:59:59'),
            ('company_id', '=', company_id),
        ]
        Move = self.env['stock.move']
        moves = Move.search(domain + [
            '|',
            ('location_dest_id.usage', '=', 'customer'),
            ('picking_code', '=', 'outgoing'),
        ])
        if warehouse_id:
            warehouse = self.env['stock.warehouse'].browse(warehouse_id)
            if warehouse.lot_stock_id:
                moves = moves.filtered(lambda m: m.location_id == warehouse.lot_stock_id or m.warehouse_id == warehouse)

        by_product = defaultdict(float)
        for move in moves:
            by_product[move.product_id.id] += abs(move.product_uom_qty)
        _logger.info('Demand aggregated products=%s company=%s', len(by_product), company_id)
        return by_product

    def sale_demand_by_product(self, date_from, date_to, company_id=None):
        """Fallback demand from sale order lines (confirmed)."""
        company_id = company_id or self.env.company.id
        lines = self.env['sale.order.line'].search([
            ('order_id.state', '=', 'sale'),
            ('order_id.company_id', '=', company_id),
            ('order_id.date_order', '>=', fields.Datetime.to_string(fields.Datetime.to_datetime(date_from))),
            ('order_id.date_order', '<=', fields.Datetime.to_string(fields.Datetime.to_datetime(date_to))[:10] + ' 23:59:59'),
            ('product_id', '!=', False),
        ])
        by_product = defaultdict(float)
        for line in lines:
            by_product[line.product_id.id] += line.product_uom_qty
        return by_product
