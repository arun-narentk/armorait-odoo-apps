# -*- coding: utf-8 -*-
"""Phase 1 inventory analytics tools (read-only)."""

from __future__ import annotations

from datetime import timedelta
from typing import Any

from odoo import fields

from .base import BaseAITool
from .registry import register_tool
from .result import tool_result


@register_tool
class NegativeStockTool(BaseAITool):
    name = 'negative_stock'
    description = 'List products with negative on-hand quantity.'

    def execute(self, arguments: dict[str, Any]) -> dict[str, Any]:
        limit = min(int(arguments.get('limit') or 20), 100)
        Product = self.env['product.product']
        Product.check_access('read')
        products = Product.search([
            ('type', '=', 'product'),
            ('qty_available', '<', 0),
        ], limit=limit, order='qty_available asc')
        return tool_result(
            headline=f'{len(products)} products with negative stock',
            summary=f'{len(products)} products are below zero on hand.',
            model='product.product',
            domain=[('type', '=', 'product'), ('qty_available', '<', 0)],
            record_ids=products.ids,
            category='inventory',
        )


@register_tool
class LowStockTool(BaseAITool):
    name = 'low_stock'
    description = 'List products with on-hand quantity below a threshold.'

    def execute(self, arguments: dict[str, Any]) -> dict[str, Any]:
        max_qty = float(arguments.get('max_qty') if arguments.get('max_qty') is not None else 10)
        limit = min(int(arguments.get('limit') or 20), 100)
        Product = self.env['product.product']
        Product.check_access('read')
        products = Product.search([
            ('type', '=', 'product'),
            ('qty_available', '<=', max_qty),
        ], limit=limit, order='qty_available asc')
        return tool_result(
            headline=f'{len(products)} low stock products',
            summary=f'{len(products)} products are at or below {max_qty} on hand.',
            model='product.product',
            domain=[('type', '=', 'product'), ('qty_available', '<=', max_qty)],
            record_ids=products.ids,
            category='inventory',
        )


@register_tool
class ProductsNotMovedTool(BaseAITool):
    name = 'products_not_moved'
    description = 'Highlight products without stock moves for a period.'

    def execute(self, arguments: dict[str, Any]) -> dict[str, Any]:
        days = int(arguments.get('days_without_move') or 90)
        limit = min(int(arguments.get('limit') or 20), 100)
        cutoff = fields.Datetime.now() - timedelta(days=days)
        Product = self.env['product.product']
        Move = self.env['stock.move']
        Product.check_access('read')
        Move.check_access('read')
        recent_move_products = Move.search([
            ('state', '=', 'done'),
            ('date', '>=', cutoff),
            ('product_id', '!=', False),
        ]).mapped('product_id').ids
        products = Product.search([
            ('type', '=', 'product'),
            ('id', 'not in', recent_move_products),
        ], limit=limit)
        return tool_result(
            headline=f'{len(products)} products not moved in {days} days',
            summary=f'{len(products)} storable products had no stock movement in the last {days} days.',
            model='product.product',
            domain=[('id', 'in', products.ids)],
            record_ids=products.ids,
            category='inventory',
        )


@register_tool
class InventoryValuationTool(BaseAITool):
    name = 'inventory_valuation'
    description = 'Estimate on-hand inventory value using standard cost.'

    def execute(self, arguments: dict[str, Any]) -> dict[str, Any]:
        limit = min(int(arguments.get('limit') or 20), 100)
        Product = self.env['product.product']
        Product.check_access('read')
        products = Product.search([('type', '=', 'product')], limit=limit)
        total_value = 0.0
        lines = []
        for product in products:
            value = product.qty_available * product.standard_price
            total_value += value
            lines.append({
                'name': product.display_name,
                'qty': product.qty_available,
                'value': value,
            })
        currency = self.env.company.currency_id.name
        return tool_result(
            headline=f'Inventory valuation: {total_value:.2f} {currency}',
            summary=f'Estimated inventory value on sampled products is {total_value:.2f} {currency}.',
            model='product.product',
            domain=[('type', '=', 'product')],
            record_ids=products.ids,
            lines=lines[:10],
            metrics=[{'label': 'Valuation', 'value': f'{total_value:.2f} {currency}'}],
            category='inventory',
        )
