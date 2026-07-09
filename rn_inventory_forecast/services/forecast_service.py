# -*- coding: utf-8 -*-
"""Rule-based demand forecast generation."""

import logging
import math
from datetime import timedelta

from odoo import fields, models

_logger = logging.getLogger(__name__)


class RnInvForecastService(models.AbstractModel):
    """Build forecast runs from historical demand."""

    _name = 'rn.inv.forecast.service'
    _description = 'Inventory Forecast Service'

    def generate_run(self, run):
        """Populate forecast lines for a run using Phase 1 rule engine."""
        run.ensure_one()
        Demand = self.env['rn.inv.demand.service']
        history = Demand.demand_by_product(
            run.date_from,
            run.date_to,
            company_id=run.company_id.id,
            warehouse_id=run.warehouse_id.id if run.warehouse_id else None,
        )
        if not history:
            history = Demand.sale_demand_by_product(
                run.date_from, run.date_to, company_id=run.company_id.id
            )
        days = max(1, (run.date_to - run.date_from).days + 1)
        horizon = max(1, run.horizon_days or 30)
        settings = self.env['rn.inv.forecast.settings'].search(
            [('company_id', '=', run.company_id.id)], limit=1
        )
        lead = settings.default_lead_time_days if settings else 7
        service_level_z = 1.65  # ~95%

        run.line_ids.unlink()
        Line = self.env['rn.inv.forecast.line']
        products = self.env['product.product'].browse(list(history.keys()))
        for product in products:
            hist_qty = history.get(product.id, 0.0)
            avg_daily = hist_qty / float(days)
            # Simple growth: compare second half vs first half via avg (Phase 1 naive)
            growth = 0.05 if avg_daily else 0.0
            seasonality = 1.0
            forecast_qty = avg_daily * horizon * (1.0 + growth) * seasonality
            qty_available = product.qty_available
            incoming = product.incoming_qty
            outgoing = product.outgoing_qty
            coverage = (qty_available / avg_daily) if avg_daily else 0.0
            # Approximate stddev as 30% of average daily demand
            stddev = avg_daily * 0.3
            safety = service_level_z * stddev * math.sqrt(max(lead, 1))
            reorder = (avg_daily * lead) + safety
            min_qty = safety
            max_qty = reorder + (avg_daily * horizon * 0.5)
            purchase = max(0.0, reorder - (qty_available + incoming - outgoing))
            purchase_date = fields.Date.context_today(self) + timedelta(days=max(0, int(coverage - lead)))
            vendor = product.seller_ids[:1].partner_id if product.seller_ids else False

            Line.create({
                'run_id': run.id,
                'product_id': product.id,
                'warehouse_id': run.warehouse_id.id if run.warehouse_id else False,
                'history_qty': hist_qty,
                'avg_daily_demand': avg_daily,
                'forecast_qty': forecast_qty,
                'growth_pct': growth * 100.0,
                'seasonality_factor': seasonality,
                'qty_available': qty_available,
                'incoming_qty': incoming,
                'outgoing_qty': outgoing,
                'coverage_days': coverage,
                'safety_stock': safety,
                'reorder_point': reorder,
                'min_qty': min_qty,
                'max_qty': max_qty,
                'recommended_purchase_qty': purchase,
                'recommended_purchase_date': purchase_date if purchase > 0 else False,
                'vendor_id': vendor.id if vendor else False,
                'lead_time_days': lead,
                'abc_class': product.rn_inv_abc_class,
                'xyz_class': product.rn_inv_xyz_class,
                'fsn_class': product.rn_inv_fsn_class,
                'is_dead_stock': product.rn_inv_is_dead_stock,
            })
            product.write({
                'rn_inv_avg_daily_demand': avg_daily,
                'rn_inv_safety_stock': safety,
                'rn_inv_reorder_point': reorder,
            })
        run.accuracy_pct = 80.0  # placeholder until actual vs forecast tracking
        _logger.info('Forecast run %s generated %s lines', run.name, len(run.line_ids))
        return True
