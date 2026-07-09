# -*- coding: utf-8 -*-
"""OWL dashboard KPI aggregation."""

import logging

from odoo import fields, models

_logger = logging.getLogger(__name__)


class RnInvDashboardService(models.AbstractModel):
    """Build inventory forecast dashboard payload."""

    _name = 'rn.inv.dashboard.service'
    _description = 'Inventory Forecast Dashboard Service'

    def get_dashboard_data(self, company_id=None):
        company_id = company_id or self.env.company.id
        Product = self.env['product.product']
        products = Product.search([('type', '=', 'consu')], limit=500)
        inventory_value = sum(
            (p.qty_available * (p.standard_price or 0.0)) for p in products
        )
        available = sum(products.mapped('qty_available'))
        incoming = sum(products.mapped('incoming_qty'))
        outgoing = sum(products.mapped('outgoing_qty'))
        dead = Product.search_count([
            ('rn_inv_is_dead_stock', '=', True),
        ])
        open_alerts = self.env['rn.inv.stock.alert'].search_count([
            ('company_id', '=', company_id),
            ('state', '=', 'open'),
        ])
        suggestions = self.env['rn.inv.reorder.suggestion'].search_count([
            ('company_id', '=', company_id),
            ('state', '=', 'recommended'),
        ])
        last_run = self.env['rn.inv.forecast.run'].search([
            ('company_id', '=', company_id),
            ('state', '=', 'done'),
        ], limit=1)
        top_moving = self.env['rn.inv.forecast.line'].search([
            ('company_id', '=', company_id),
        ], order='forecast_qty desc', limit=10)
        return {
            'cards': {
                'inventory_value': inventory_value,
                'available_stock': available,
                'incoming_stock': incoming,
                'outgoing_stock': outgoing,
                'forecast_accuracy': last_run.accuracy_pct if last_run else 0.0,
                'open_alerts': open_alerts,
                'dead_stock': dead,
                'reorder_suggestions': suggestions,
                'stock_coverage': 0.0,
            },
            'tops': {
                'products': [
                    {
                        'name': line.product_id.display_name,
                        'value': line.forecast_qty,
                    }
                    for line in top_moving
                ],
            },
            'warehouse': [],
            'updated_at': fields.Datetime.to_string(fields.Datetime.now()),
        }
