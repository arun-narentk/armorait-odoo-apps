# -*- coding: utf-8 -*-
"""Smart inventory alerts."""

import logging

from odoo import fields, models

_logger = logging.getLogger(__name__)


class RnInvAlertService(models.AbstractModel):
    """Generate low / over / dead / negative stock alerts."""

    _name = 'rn.inv.alert.service'
    _description = 'Inventory Alert Service'

    def scan_alerts(self, company_id=None):
        company_id = company_id or self.env.company.id
        settings = self.env['rn.inv.forecast.settings'].search(
            [('company_id', '=', company_id)], limit=1
        )
        if settings and not settings.enable_alerts:
            return self.env['rn.inv.stock.alert']
        low_days = settings.low_stock_coverage_days if settings else 7.0
        over_days = settings.overstock_coverage_days if settings else 90.0
        Alert = self.env['rn.inv.stock.alert']
        created = Alert
        products = self.env['product.product'].search([
            ('type', '=', 'consu'),
        ], limit=500)
        for product in products:
            qty = product.qty_available
            avg = product.rn_inv_avg_daily_demand or 0.0
            coverage = (qty / avg) if avg else None
            if qty < 0:
                created |= Alert.create({
                    'name': 'Negative stock: %s' % product.display_name,
                    'alert_type': 'negative',
                    'severity': 'critical',
                    'product_id': product.id,
                    'company_id': company_id,
                    'qty': qty,
                    'message': 'Product has negative on-hand quantity.',
                })
            elif product.rn_inv_is_dead_stock:
                created |= Alert.create({
                    'name': 'Dead stock: %s' % product.display_name,
                    'alert_type': 'dead',
                    'severity': 'warning',
                    'product_id': product.id,
                    'company_id': company_id,
                    'qty': qty,
                    'message': 'No recent movement detected.',
                })
            elif coverage is not None and coverage < low_days:
                created |= Alert.create({
                    'name': 'Low stock: %s' % product.display_name,
                    'alert_type': 'low',
                    'severity': 'warning',
                    'product_id': product.id,
                    'company_id': company_id,
                    'qty': qty,
                    'message': 'Coverage below %s days.' % low_days,
                })
            elif coverage is not None and coverage > over_days:
                created |= Alert.create({
                    'name': 'Overstock: %s' % product.display_name,
                    'alert_type': 'over',
                    'severity': 'info',
                    'product_id': product.id,
                    'company_id': company_id,
                    'qty': qty,
                    'message': 'Coverage above %s days.' % over_days,
                })
            elif product.rn_inv_reorder_point and qty <= product.rn_inv_reorder_point:
                created |= Alert.create({
                    'name': 'Reorder reminder: %s' % product.display_name,
                    'alert_type': 'reorder',
                    'severity': 'warning',
                    'product_id': product.id,
                    'company_id': company_id,
                    'qty': qty,
                    'message': 'On-hand at or below reorder point.',
                })
        _logger.info('Alerts created=%s company=%s', len(created), company_id)
        return created
