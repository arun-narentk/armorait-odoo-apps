# -*- coding: utf-8 -*-
"""Chart dataset builders for Chart.js widgets."""

import logging
from collections import defaultdict

from odoo import models

_logger = logging.getLogger(__name__)


class RnBiChartService(models.AbstractModel):
    """Transform sales orders into chart-friendly series."""

    _name = 'rn.bi.chart.service'
    _description = 'BI Chart Service'

    def build_chart_bundle(self, orders, date_from, date_to):
        """Return line/bar/pie stub datasets for OWL Chart.js bindings."""
        by_day = defaultdict(float)
        by_user = defaultdict(float)
        by_categ = defaultdict(float)
        for order in orders:
            day = order.date_order.date().isoformat() if order.date_order else 'unknown'
            by_day[day] += order.amount_untaxed
            user_name = order.user_id.name or 'Unassigned'
            by_user[user_name] += order.amount_untaxed
            for line in order.order_line:
                categ = line.product_id.categ_id.name if line.product_id.categ_id else 'Other'
                by_categ[categ] += line.price_subtotal
        return {
            'monthly_trend': {
                'type': 'line',
                'labels': sorted(by_day.keys()),
                'datasets': [{'label': 'Revenue', 'data': [by_day[k] for k in sorted(by_day.keys())]}],
            },
            'salesperson': {
                'type': 'bar',
                'labels': list(by_user.keys()),
                'datasets': [{'label': 'Sales', 'data': list(by_user.values())}],
            },
            'category': {
                'type': 'pie',
                'labels': list(by_categ.keys()),
                'datasets': [{'label': 'Category', 'data': list(by_categ.values())}],
            },
        }

    def build_top_lists(self, orders, limit=10):
        """Top products/customers/salespersons."""
        products = defaultdict(float)
        customers = defaultdict(float)
        users = defaultdict(float)
        for order in orders:
            customers[order.partner_id.display_name] += order.amount_untaxed
            users[order.user_id.name or 'Unassigned'] += order.amount_untaxed
            for line in order.order_line:
                products[line.product_id.display_name] += line.price_subtotal

        def top(data):
            items = sorted(data.items(), key=lambda x: x[1], reverse=True)[:limit]
            return [{'name': n, 'value': v} for n, v in items]

        return {
            'products': top(products),
            'customers': top(customers),
            'salespersons': top(users),
        }
