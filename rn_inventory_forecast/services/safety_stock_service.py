# -*- coding: utf-8 -*-
"""Safety stock / reorder point calculator."""

import logging
import math

from odoo import fields, models

_logger = logging.getLogger(__name__)


class RnInvSafetyStockService(models.AbstractModel):
    """Compute safety stock recommendations."""

    _name = 'rn.inv.safety.stock.service'
    _description = 'Inventory Safety Stock Service'

    def compute_for_company(self, company_id=None):
        company_id = company_id or self.env.company.id
        settings = self.env['rn.inv.forecast.settings'].search(
            [('company_id', '=', company_id)], limit=1
        )
        lead = settings.default_lead_time_days if settings else 7
        z = 1.65
        date_from, date_to = self.env['rn.inv.demand.service'].get_history_window(company_id)
        demand = self.env['rn.inv.demand.service'].sale_demand_by_product(
            date_from, date_to, company_id=company_id
        )
        days = max(1, (date_to - date_from).days + 1)
        Safety = self.env['rn.inv.safety.stock']
        created = Safety
        for product_id, qty in demand.items():
            product = self.env['product.product'].browse(product_id)
            avg = qty / float(days)
            stddev = avg * 0.3
            safety = z * stddev * math.sqrt(max(lead, 1))
            reorder = (avg * lead) + safety
            created |= Safety.create({
                'name': 'Safety %s' % product.display_name,
                'product_id': product.id,
                'company_id': company_id,
                'avg_daily_demand': avg,
                'demand_stddev': stddev,
                'lead_time_days': lead,
                'service_level': 0.95,
                'safety_qty': safety,
                'reorder_point': reorder,
                'min_qty': safety,
                'max_qty': reorder + avg * 30,
                'computation_date': fields.Datetime.now(),
            })
            product.write({
                'rn_inv_safety_stock': safety,
                'rn_inv_reorder_point': reorder,
                'rn_inv_avg_daily_demand': avg,
            })
        _logger.info('Safety stock computed rows=%s', len(created))
        return created
