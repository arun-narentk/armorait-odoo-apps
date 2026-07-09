# -*- coding: utf-8 -*-
"""XYZ analysis (demand variability)."""

import logging

from odoo import fields, models

_logger = logging.getLogger(__name__)


class RnInvXyzService(models.AbstractModel):
    """Classify products by demand variability (Phase 1 approximation)."""

    _name = 'rn.inv.xyz.service'
    _description = 'Inventory XYZ Service'

    def run_analysis(self, date_from, date_to, company_id=None, warehouse_id=None):
        company_id = company_id or self.env.company.id
        # Split period into weekly buckets and measure CV of weekly demand
        demand_daily = self.env['rn.inv.demand.service'].sale_demand_by_product(
            date_from, date_to, company_id=company_id
        )
        Analysis = self.env['rn.inv.analysis']
        created = Analysis
        today = fields.Date.context_today(self)
        days = max(1, (date_to - date_from).days + 1)
        for product_id, qty in demand_daily.items():
            product = self.env['product.product'].browse(product_id)
            avg = qty / float(days)
            # Phase 1: treat higher volume as lower variability X, mid Y, sparse Z
            if avg >= 2:
                code = 'X'
                score = 0.2
            elif avg >= 0.5:
                code = 'Y'
                score = 0.5
            else:
                code = 'Z'
                score = 0.9
            product.rn_inv_xyz_class = code
            created |= Analysis.create({
                'name': 'XYZ %s' % product.display_name,
                'analysis_type': 'xyz',
                'analysis_date': today,
                'date_from': date_from,
                'date_to': date_to,
                'product_id': product.id,
                'warehouse_id': warehouse_id,
                'company_id': company_id,
                'value': score,
                'qty': qty,
                'class_code': code,
            })
        _logger.info('XYZ analysis created %s rows', len(created))
        return created
