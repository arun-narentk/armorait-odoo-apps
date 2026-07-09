# -*- coding: utf-8 -*-
"""FSN and dead stock analysis."""

import logging
from datetime import timedelta

from odoo import fields, models

_logger = logging.getLogger(__name__)


class RnInvFsnService(models.AbstractModel):
    """Classify Fast / Slow / Non-moving and detect dead stock."""

    _name = 'rn.inv.fsn.service'
    _description = 'Inventory FSN Service'

    def run_analysis(self, date_from, date_to, company_id=None, warehouse_id=None):
        company_id = company_id or self.env.company.id
        settings = self.env['rn.inv.forecast.settings'].search(
            [('company_id', '=', company_id)], limit=1
        )
        dead_days = settings.dead_stock_days if settings else 90
        demand = self.env['rn.inv.demand.service'].sale_demand_by_product(
            date_from, date_to, company_id=company_id
        )
        days = max(1, (date_to - date_from).days + 1)
        Analysis = self.env['rn.inv.analysis']
        created = Analysis
        today = fields.Date.context_today(self)
        for product_id, qty in demand.items():
            product = self.env['product.product'].browse(product_id)
            avg = qty / float(days)
            if avg >= 1.0:
                code = 'fast'
            elif avg > 0:
                code = 'slow'
            else:
                code = 'non'
            product.rn_inv_fsn_class = code
            product.rn_inv_is_dead_stock = False
            created |= Analysis.create({
                'name': 'FSN %s' % product.display_name,
                'analysis_type': 'fsn',
                'analysis_date': today,
                'date_from': date_from,
                'date_to': date_to,
                'product_id': product.id,
                'warehouse_id': warehouse_id,
                'company_id': company_id,
                'value': avg,
                'qty': qty,
                'class_code': code,
            })

        # Dead stock: on-hand with no demand in dead_days window
        dead_from = today - timedelta(days=dead_days)
        products = self.env['product.product'].search([
            ('qty_available', '>', 0),
            ('type', '=', 'consu'),
        ], limit=500)
        dead_demand = self.env['rn.inv.demand.service'].sale_demand_by_product(
            dead_from, today, company_id=company_id
        )
        for product in products:
            if product.id not in dead_demand:
                product.rn_inv_is_dead_stock = True
                product.rn_inv_fsn_class = 'non'
                created |= Analysis.create({
                    'name': 'Dead %s' % product.display_name,
                    'analysis_type': 'dead',
                    'analysis_date': today,
                    'date_from': dead_from,
                    'date_to': today,
                    'product_id': product.id,
                    'warehouse_id': warehouse_id,
                    'company_id': company_id,
                    'value': product.qty_available * (product.standard_price or 0.0),
                    'qty': product.qty_available,
                    'class_code': 'dead',
                })
        _logger.info('FSN/dead analysis created %s rows', len(created))
        return created
