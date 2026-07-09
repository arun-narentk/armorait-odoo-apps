# -*- coding: utf-8 -*-
"""Phase 1 accounting analytics tools (read-only)."""

from __future__ import annotations

from datetime import timedelta
from typing import Any

from dateutil.relativedelta import relativedelta

from odoo import fields

from .base import BaseAITool
from .registry import register_tool
from .result import tool_result


@register_tool
class OverdueInvoicesTool(BaseAITool):
    name = 'overdue_invoices'
    description = 'List posted customer invoices unpaid past their due date.'

    def execute(self, arguments: dict[str, Any]) -> dict[str, Any]:
        days = int(arguments.get('days_overdue') if arguments.get('days_overdue') is not None else 0)
        limit = min(int(arguments.get('limit') or 20), 50)
        cutoff = fields.Date.today() - timedelta(days=days)
        Move = self.env['account.move']
        Move.check_access('read')
        domain = [
            ('move_type', '=', 'out_invoice'),
            ('state', '=', 'posted'),
            ('payment_state', 'in', ('not_paid', 'partial')),
            ('invoice_date_due', '<=', cutoff),
        ]
        invoices = Move.search(domain, limit=limit, order='invoice_date_due asc')
        total_residual = sum(invoices.mapped('amount_residual'))
        currency = self.env.company.currency_id.name
        return tool_result(
            headline=f'{len(invoices)} overdue invoices',
            summary=(
                f'{len(invoices)} overdue invoices with '
                f'{total_residual:.2f} {currency} still outstanding.'
            ),
            model='account.move',
            domain=domain,
            record_ids=invoices.ids,
            metrics=[{'label': 'Outstanding', 'value': f'{total_residual:.2f} {currency}'}],
            lines=[{
                'name': invoice.name,
                'partner': invoice.partner_id.display_name,
                'amount': invoice.amount_residual,
            } for invoice in invoices[:5]],
            category='accounting',
        )


@register_tool
class CustomerBalanceTool(BaseAITool):
    name = 'customer_balance'
    description = 'Show customers with the highest receivable balances.'

    def execute(self, arguments: dict[str, Any]) -> dict[str, Any]:
        limit = min(int(arguments.get('limit') or 10), 20)
        Partner = self.env['res.partner']
        Partner.check_access('read')
        partners = Partner.search([
            ('customer_rank', '>', 0),
            ('credit', '>', 0),
        ], limit=limit, order='credit desc')
        total = sum(partners.mapped('credit'))
        return tool_result(
            headline=f'{len(partners)} customers with balance',
            summary=f'Customers with outstanding receivables totaling {total:.2f}.',
            model='res.partner',
            domain=[('id', 'in', partners.ids)],
            record_ids=partners.ids,
            lines=[{'name': p.name, 'balance': p.credit} for p in partners],
            category='accounting',
        )


@register_tool
class RevenueThisMonthTool(BaseAITool):
    name = 'revenue_this_month'
    description = 'Show posted customer invoice revenue for the current month.'

    def execute(self, arguments: dict[str, Any]) -> dict[str, Any]:
        today = fields.Date.today()
        start = today.replace(day=1)
        end = start + relativedelta(months=1, days=-1)
        Move = self.env['account.move']
        Move.check_access('read')
        domain = [
            ('move_type', '=', 'out_invoice'),
            ('state', '=', 'posted'),
            ('invoice_date', '>=', start),
            ('invoice_date', '<=', end),
        ]
        invoices = Move.search(domain)
        revenue = sum(invoices.mapped('amount_untaxed'))
        currency = self.env.company.currency_id.name
        return tool_result(
            headline=f'Revenue this month: {revenue:.2f} {currency}',
            summary=f'Posted customer invoice revenue this month is {revenue:.2f} {currency}.',
            model='account.move',
            domain=domain,
            record_ids=invoices.ids,
            metrics=[{'label': 'Revenue', 'value': f'{revenue:.2f} {currency}'}],
            category='accounting',
        )


@register_tool
class ExpensesThisMonthTool(BaseAITool):
    name = 'expenses_this_month'
    description = 'Show posted vendor bill totals for the current month.'

    def execute(self, arguments: dict[str, Any]) -> dict[str, Any]:
        today = fields.Date.today()
        start = today.replace(day=1)
        end = start + relativedelta(months=1, days=-1)
        Move = self.env['account.move']
        Move.check_access('read')
        domain = [
            ('move_type', '=', 'in_invoice'),
            ('state', '=', 'posted'),
            ('invoice_date', '>=', start),
            ('invoice_date', '<=', end),
        ]
        bills = Move.search(domain)
        expenses = sum(bills.mapped('amount_untaxed'))
        currency = self.env.company.currency_id.name
        return tool_result(
            headline=f'Expenses this month: {expenses:.2f} {currency}',
            summary=f'Posted vendor bills this month total {expenses:.2f} {currency}.',
            model='account.move',
            domain=domain,
            record_ids=bills.ids,
            category='accounting',
        )


@register_tool
class ProfitThisMonthTool(BaseAITool):
    name = 'profit_this_month'
    description = 'Estimate profit as customer revenue minus vendor expenses this month.'

    def execute(self, arguments: dict[str, Any]) -> dict[str, Any]:
        revenue_tool = RevenueThisMonthTool(self.env)
        expense_tool = ExpensesThisMonthTool(self.env)
        revenue = revenue_tool.execute({})
        expenses = expense_tool.execute({})
        rev_value = sum(
            self.env['account.move'].browse(revenue.get('record_ids', [])).mapped('amount_untaxed')
        )
        exp_value = sum(
            self.env['account.move'].browse(expenses.get('record_ids', [])).mapped('amount_untaxed')
        )
        profit = rev_value - exp_value
        currency = self.env.company.currency_id.name
        return tool_result(
            headline=f'Profit this month: {profit:.2f} {currency}',
            summary=(
                f'Estimated profit this month is {profit:.2f} {currency} '
                f'(revenue {rev_value:.2f}, expenses {exp_value:.2f}).'
            ),
            metrics=[
                {'label': 'Revenue', 'value': f'{rev_value:.2f} {currency}'},
                {'label': 'Expenses', 'value': f'{exp_value:.2f} {currency}'},
                {'label': 'Profit', 'value': f'{profit:.2f} {currency}'},
            ],
            category='accounting',
        )


@register_tool
class RevenueAnalysisTool(BaseAITool):
    name = 'revenue_analysis'
    description = 'Compare customer invoice revenue between this month and last month.'

    def execute(self, arguments: dict[str, Any]) -> dict[str, Any]:
        offset = int(arguments.get('month_offset') or 0)
        today = fields.Date.today()
        current_start = today.replace(day=1) - relativedelta(months=offset)
        current_end = current_start + relativedelta(months=1, days=-1)
        previous_start = current_start - relativedelta(months=1)
        previous_end = current_start - relativedelta(days=1)
        Move = self.env['account.move']
        Move.check_access('read')
        base_domain = [('move_type', '=', 'out_invoice'), ('state', '=', 'posted')]

        def _sum_period(start, end):
            records = Move.search(base_domain + [
                ('invoice_date', '>=', start),
                ('invoice_date', '<=', end),
            ])
            return sum(records.mapped('amount_untaxed')), records

        current_revenue, current_records = _sum_period(current_start, current_end)
        previous_revenue, _previous_records = _sum_period(previous_start, previous_end)
        delta = current_revenue - previous_revenue
        pct = round((delta / previous_revenue) * 100, 2) if previous_revenue else None
        if delta == 0:
            summary = 'Revenue is unchanged compared to last month.'
        elif delta > 0:
            summary = f'Revenue increased by {pct}% compared to last month.'
        else:
            summary = f'Revenue decreased by {abs(pct)}% compared to last month.'
        return tool_result(
            headline='Revenue comparison',
            summary=summary,
            model='account.move',
            domain=base_domain + [
                ('invoice_date', '>=', current_start),
                ('invoice_date', '<=', current_end),
            ],
            record_ids=current_records.ids,
            metrics=[
                {'label': 'This month', 'value': f'{current_revenue:.2f}'},
                {'label': 'Last month', 'value': f'{previous_revenue:.2f}'},
                {'label': 'Change', 'value': f'{delta:.2f}'},
            ],
            category='accounting',
        )
