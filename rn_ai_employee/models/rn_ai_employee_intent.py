# -*- coding: utf-8 -*-
"""Business-first intent detection. Maps natural language to analytics tools."""

from __future__ import annotations

import re
from typing import Any

from odoo import api, models


class AiEmployeeIntent(models.AbstractModel):
    _name = 'rn.ai.employee.intent'
    _description = 'AI Employee Intent Detector'

    # Higher priority wins when multiple rules match.
    INTENT_RULES = (
        {'tool': 'overdue_invoices', 'priority': 100, 'phrases': (
            'overdue invoice', 'unpaid invoice', 'past due', 'not paid',
        )},
        {'tool': 'today_sales', 'priority': 95, 'phrases': (
            "today's sales", 'todays sales', 'sales today', 'today sales', 'show today sales',
        )},
        {'tool': 'pending_quotations', 'priority': 94, 'phrases': (
            'pending quotation', 'open quotation', 'draft quotation', 'waiting quotation',
        )},
        {'tool': 'lost_quotations', 'priority': 93, 'phrases': (
            'lost quotation', 'cancelled quotation', 'canceled quotation',
        )},
        {'tool': 'top_customers', 'priority': 92, 'phrases': (
            'top customer', 'best customer', 'largest customer',
        )},
        {'tool': 'best_selling_products', 'priority': 91, 'phrases': (
            'best selling', 'top product', 'bestseller', 'most sold',
        )},
        {'tool': 'revenue_this_month', 'priority': 90, 'phrases': (
            'revenue this month', 'monthly revenue', 'sales this month',
        )},
        {'tool': 'revenue_analysis', 'priority': 89, 'phrases': (
            'revenue decrease', 'revenue fell', 'revenue drop', 'why did revenue',
        )},
        {'tool': 'customer_balance', 'priority': 88, 'phrases': (
            'customer balance', 'receivable', 'outstanding balance',
        )},
        {'tool': 'expenses_this_month', 'priority': 87, 'phrases': (
            'expenses this month', 'monthly expense', 'spend this month',
        )},
        {'tool': 'profit_this_month', 'priority': 86, 'phrases': (
            'profit this month', 'margin this month', 'net profit',
        )},
        {'tool': 'negative_stock', 'priority': 85, 'phrases': (
            'negative stock', 'below zero', 'stock negative',
        )},
        {'tool': 'low_stock', 'priority': 84, 'phrases': (
            'low stock', 'stock issue', 'running low', 'reorder',
        )},
        {'tool': 'products_not_moved', 'priority': 83, 'phrases': (
            'not moved', 'dead stock', 'slow moving', 'no movement',
        )},
        {'tool': 'inventory_valuation', 'priority': 82, 'phrases': (
            'inventory valuation', 'stock value', 'inventory value',
        )},
        {'tool': 'find_customer', 'priority': 70, 'phrases': (
            'find customer', 'search customer', 'inactive customer', 'customer inactive',
        )},
        {'tool': 'top_opportunities', 'priority': 81, 'phrases': (
            'top opportunit', 'best deal', 'pipeline top',
        )},
        {'tool': 'lost_leads', 'priority': 80, 'phrases': (
            'lost lead', 'lead lost',
        )},
        {'tool': 'followup_overdue', 'priority': 79, 'phrases': (
            'follow up overdue', 'follow-up overdue', 'overdue followup',
        )},
        {'tool': 'pipeline_revenue', 'priority': 78, 'phrases': (
            'expected revenue', 'pipeline revenue', 'forecast revenue',
        )},
    )

    @api.model
    def detect(self, user_text: str) -> tuple[str | None, dict[str, Any]]:
        """Return (tool_name, arguments) for a user question."""
        normalized = self._normalize(user_text)
        if not normalized:
            return None, {}

        direct = self._match_suggestion_question(user_text)
        if direct:
            return direct

        best_tool = None
        best_priority = -1
        for rule in self.INTENT_RULES:
            if any(phrase in normalized for phrase in rule['phrases']):
                if rule['priority'] > best_priority:
                    best_tool = rule['tool']
                    best_priority = rule['priority']

        if not best_tool:
            return None, {}

        return best_tool, self._default_arguments(best_tool, normalized)

    @api.model
    def _match_suggestion_question(self, user_text: str) -> tuple[str | None, dict[str, Any]] | None:
        suggestion = self.env['rn.ai.employee.suggestion'].search([
            ('question', '=ilike', user_text.strip()),
            ('active', '=', True),
        ], limit=1)
        if suggestion and suggestion.tool_name:
            return suggestion.tool_name, suggestion.get_tool_arguments()
        return None

    @api.model
    def _default_arguments(self, tool_name: str, normalized_text: str) -> dict[str, Any]:
        args: dict[str, Any] = {}
        if tool_name == 'overdue_invoices':
            args['days_overdue'] = 0
        if tool_name == 'find_customer':
            args['inactive_months'] = 6 if 'inactive' in normalized_text or '6 month' in normalized_text else 0
        if 'limit' not in args:
            args['limit'] = 20
        return args

    @staticmethod
    def _normalize(text: str) -> str:
        lowered = (text or '').strip().lower()
        return re.sub(r'\s+', ' ', lowered)
