# -*- coding: utf-8 -*-

from datetime import date

from odoo import api, fields, models
from odoo.tools import float_round


class ProductProduct(models.Model):
    _inherit = 'product.product'

    last_outgoing_date = fields.Date(
        string='Last Outgoing Date',
        help='Date of last outgoing stock move (to customer).',
        copy=False,
    )
    dead_stock_days = fields.Integer(
        string='Days Without Movement',
        help='Days since last outgoing move.',
        copy=False,
    )
    dead_stock_status = fields.Selection(
        [
            ('healthy', 'Healthy'),
            ('slow', 'Slow Moving'),
            ('dead', 'Dead Stock'),
        ],
        string='Dead Stock Status',
        copy=False,
        index=True,
    )
    inventory_carrying_cost = fields.Float(
        string='Carrying Cost (Est.)',
        digits='Product Price',
        copy=False,
        help='Estimated carrying cost (interest + storage) for current stock.',
    )
    capital_locked = fields.Float(
        string='Capital Locked',
        compute='_compute_capital_locked',
        store=True,
        digits='Product Price',
        help='qty_available × standard_price.',
    )

    @api.depends('qty_available', 'standard_price')
    def _compute_capital_locked(self):
        for p in self:
            p.capital_locked = float_round(p.qty_available * p.standard_price, precision_digits=2)

    @api.model
    def _cron_recompute_dead_stock_metrics(self):
        """Nightly cron: set last_outgoing_date, dead_stock_days, dead_stock_status, inventory_carrying_cost."""
        products = self.search([('type', '=', 'product')])
        products._recompute_dead_stock_metrics()

    def _recompute_dead_stock_metrics(self):
        """Update dead stock fields for given products (used by cron or after stock move)."""
        if not self:
            return
        ICP = self.env['ir.config_parameter'].sudo()
        days_slow = int(ICP.get_param('rn_profit_guard.dead_stock_days_slow', 90))
        days_dead = int(ICP.get_param('rn_profit_guard.dead_stock_days_dead', 180))
        carrying_pct = float(ICP.get_param('rn_profit_guard.carrying_cost_annual_pct', 15))
        today = date.today()
        product_ids = self.ids
        self.env.cr.execute("""
            SELECT product_id, MAX(date) AS last_date
            FROM stock_move
            WHERE state = 'done'
              AND product_id = ANY(%s)
              AND location_dest_id IN (
                  SELECT id FROM stock_location
                  WHERE usage IN ('customer', 'consignment')
              )
            GROUP BY product_id
        """, (product_ids,))
        last_by_product = {}
        for row in self.env.cr.fetchall():
            d = row[1]
            if d and hasattr(d, 'date') and callable(d.date):
                d = d.date()
            last_by_product[row[0]] = d
        to_write = []
        for product in self:
            last_date = last_by_product.get(product.id)
            if last_date:
                days = (today - last_date).days
            else:
                days = 9999
            if days >= days_dead:
                status = 'dead'
            elif days >= days_slow:
                status = 'slow'
            else:
                status = 'healthy'
            capital = product.qty_available * product.standard_price
            carrying = float_round(
                capital * (carrying_pct / 100.0) * (min(days, 365) / 365.0),
                precision_digits=2,
            )
            to_write.append((product.id, {
                'last_outgoing_date': last_date,
                'dead_stock_days': min(days, 9999) if last_date else 0,
                'dead_stock_status': status,
                'inventory_carrying_cost': carrying,
            }))
        for pid, vals in to_write:
            self.browse(pid).write(vals)
