# -*- coding: utf-8 -*-
"""Turn structured tool output into manager-friendly explanations."""

from __future__ import annotations

from typing import Any

from odoo import _, api, models


class AiEmployeeExplainer(models.AbstractModel):
    _name = 'rn.ai.employee.explainer'
    _description = 'AI Employee Result Explainer'

    @api.model
    def explain(self, tool_name: str, result: dict[str, Any]) -> str:
        """Produce the assistant message body. Templates only, no LLM in Phase 1."""
        if result.get('error'):
            return result['error']
        if result.get('summary'):
            return result['summary']

        explainers = {
            'overdue_invoices': self._explain_overdue_invoices,
            'today_sales': self._explain_today_sales,
            'pending_quotations': self._explain_count_headline,
            'lost_quotations': self._explain_count_headline,
            'top_customers': self._explain_top_customers,
            'best_selling_products': self._explain_lines,
            'revenue_this_month': self._explain_revenue_month,
            'revenue_analysis': self._explain_revenue_analysis,
            'customer_balance': self._explain_lines,
            'expenses_this_month': self._explain_expenses,
            'profit_this_month': self._explain_profit,
            'negative_stock': self._explain_count_headline,
            'low_stock': self._explain_count_headline,
            'products_not_moved': self._explain_count_headline,
            'inventory_valuation': self._explain_inventory_valuation,
            'find_customer': self._explain_find_customer,
            'top_opportunities': self._explain_lines,
            'lost_leads': self._explain_count_headline,
            'followup_overdue': self._explain_count_headline,
            'pipeline_revenue': self._explain_pipeline,
            'create_quotation': self._explain_count_headline,
            'send_payment_reminders': self._explain_count_headline,
        }
        handler = explainers.get(tool_name, self._explain_generic)
        return handler(result)

    @api.model
    def _explain_generic(self, result: dict[str, Any]) -> str:
        return result.get('headline') or _('Here are the results.')

    @api.model
    def _explain_overdue_invoices(self, result: dict[str, Any]) -> str:
        return _(
            '%(headline)s\n\nTotal outstanding: %(total)s\n'
            'Review the list and follow up with customers who need payment reminders.'
        ) % {
            'headline': result.get('headline'),
            'total': result.get('metrics', [{}])[0].get('value', '0'),
        }

    @api.model
    def _explain_today_sales(self, result: dict[str, Any]) -> str:
        return _(
            '%(headline)s\n\nOrders today: %(orders)s\nRevenue today: %(revenue)s'
        ) % {
            'headline': result.get('headline'),
            'orders': result.get('metrics', [{}, {}])[0].get('value', 0),
            'revenue': result.get('metrics', [{}, {}])[1].get('value', 0),
        }

    @api.model
    def _explain_count_headline(self, result: dict[str, Any]) -> str:
        return result.get('summary') or result.get('headline', '')

    @api.model
    def _explain_top_customers(self, result: dict[str, Any]) -> str:
        lines = result.get('lines') or []
        names = ', '.join(line.get('name', '') for line in lines[:3])
        return _('%s\n\nTop customers: %s') % (result.get('headline', ''), names or _('none'))

    @api.model
    def _explain_lines(self, result: dict[str, Any]) -> str:
        return result.get('summary') or result.get('headline', '')

    @api.model
    def _explain_revenue_month(self, result: dict[str, Any]) -> str:
        return result.get('summary') or result.get('headline', '')

    @api.model
    def _explain_revenue_analysis(self, result: dict[str, Any]) -> str:
        return result.get('summary') or result.get('headline', '')

    @api.model
    def _explain_expenses(self, result: dict[str, Any]) -> str:
        return result.get('summary') or result.get('headline', '')

    @api.model
    def _explain_profit(self, result: dict[str, Any]) -> str:
        return result.get('summary') or result.get('headline', '')

    @api.model
    def _explain_inventory_valuation(self, result: dict[str, Any]) -> str:
        return result.get('summary') or result.get('headline', '')

    @api.model
    def _explain_find_customer(self, result: dict[str, Any]) -> str:
        return result.get('summary') or result.get('headline', '')

    @api.model
    def _explain_pipeline(self, result: dict[str, Any]) -> str:
        return result.get('summary') or result.get('headline', '')
