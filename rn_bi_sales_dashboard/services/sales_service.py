# -*- coding: utf-8 -*-
"""Sales data aggregation helpers."""

import logging
from datetime import datetime, time

from odoo import fields, models

_logger = logging.getLogger(__name__)


class RnBiSalesService(models.AbstractModel):
    """Query sales orders and CRM opportunities for KPI engines."""

    _name = 'rn.bi.sales.service'
    _description = 'BI Sales Service'

    def _date_bounds(self, date_from, date_to):
        """Convert dates to datetime bounds for sale.order date_order."""
        start = fields.Datetime.to_datetime(date_from) if date_from else False
        end = fields.Datetime.to_datetime(date_to) if date_to else False
        if end and not isinstance(end, datetime):
            end = datetime.combine(end, time.max)
        elif end:
            end = datetime.combine(end.date(), time.max)
        return start, end

    def search_orders(self, date_from=None, date_to=None, domain=None, states=None):
        """Return confirmed/quotation orders matching filters."""
        states = states or ['sale']
        order_domain = [('state', 'in', states)]
        start, end = self._date_bounds(date_from, date_to)
        if start:
            order_domain.append(('date_order', '>=', fields.Datetime.to_string(start)))
        if end:
            order_domain.append(('date_order', '<=', fields.Datetime.to_string(end)))
        if domain:
            order_domain += domain
        return self.env['sale.order'].search(order_domain)

    def summarize_orders(self, orders):
        """Compute revenue/orders/aov from a recordset."""
        revenue = sum(orders.mapped('amount_untaxed'))
        count = len(orders)
        partners = orders.mapped('partner_id')
        return {
            'revenue': revenue,
            'orders': count,
            'aov': (revenue / count) if count else 0.0,
            'customers': len(partners),
        }
