# -*- coding: utf-8 -*-
"""ABC analysis (value contribution)."""

import logging

from odoo import fields, models

_logger = logging.getLogger(__name__)


class RnInvAbcService(models.AbstractModel):
    """Classify products A/B/C by cumulative demand value."""

    _name = 'rn.inv.abc.service'
    _description = 'Inventory ABC Service'

    def run_analysis(self, date_from, date_to, company_id=None, warehouse_id=None):
        company_id = company_id or self.env.company.id
        settings = self.env['rn.inv.forecast.settings'].search(
            [('company_id', '=', company_id)], limit=1
        )
        a_pct = settings.abc_a_pct if settings else 80.0
        b_pct = settings.abc_b_pct if settings else 95.0
        demand = self.env['rn.inv.demand.service'].sale_demand_by_product(
            date_from, date_to, company_id=company_id
        )
        rows = []
        for product_id, qty in demand.items():
            product = self.env['product.product'].browse(product_id)
            value = qty * (product.list_price or product.standard_price or 0.0)
            rows.append((product, qty, value))
        rows.sort(key=lambda r: r[2], reverse=True)
        total = sum(r[2] for r in rows) or 1.0
        cumulative = 0.0
        Analysis = self.env['rn.inv.analysis']
        created = self.env['rn.inv.analysis']
        today = fields.Date.context_today(self)
        for product, qty, value in rows:
            cumulative += value
            share = (cumulative / total) * 100.0
            if share <= a_pct:
                code = 'A'
            elif share <= b_pct:
                code = 'B'
            else:
                code = 'C'
            product.rn_inv_abc_class = code
            created |= Analysis.create({
                'name': 'ABC %s' % product.display_name,
                'analysis_type': 'abc',
                'analysis_date': today,
                'date_from': date_from,
                'date_to': date_to,
                'product_id': product.id,
                'warehouse_id': warehouse_id,
                'company_id': company_id,
                'value': value,
                'qty': qty,
                'class_code': code,
            })
        _logger.info('ABC analysis created %s rows', len(created))
        return created
