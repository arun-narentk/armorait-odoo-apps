# -*- coding: utf-8 -*-
"""Purchase / reorder suggestion builder."""

import logging
from datetime import timedelta

from odoo import fields, models

_logger = logging.getLogger(__name__)


class RnInvReorderService(models.AbstractModel):
    """Create reorder suggestions below reorder point."""

    _name = 'rn.inv.reorder.service'
    _description = 'Inventory Reorder Service'

    def generate_suggestions(self, company_id=None):
        company_id = company_id or self.env.company.id
        settings = self.env['rn.inv.forecast.settings'].search(
            [('company_id', '=', company_id)], limit=1
        )
        lead = settings.default_lead_time_days if settings else 7
        products = self.env['product.product'].search([
            ('rn_inv_reorder_point', '>', 0),
        ])
        Suggestion = self.env['rn.inv.reorder.suggestion']
        created = Suggestion
        today = fields.Date.context_today(self)
        for product in products:
            available = product.qty_available + product.incoming_qty
            if available >= product.rn_inv_reorder_point:
                continue
            qty = max(0.0, product.rn_inv_reorder_point - available + (product.rn_inv_safety_stock or 0.0))
            vendor = product.seller_ids[:1].partner_id if product.seller_ids else False
            created |= Suggestion.create({
                'name': 'Reorder %s' % product.display_name,
                'product_id': product.id,
                'company_id': company_id,
                'vendor_id': vendor.id if vendor else False,
                'qty_to_order': qty,
                'recommended_date': today,
                'lead_time_days': lead,
                'safety_refill': True,
                'state': 'recommended',
            })
        _logger.info('Reorder suggestions created=%s', len(created))
        return created
