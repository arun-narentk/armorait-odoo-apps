# -*- coding: utf-8 -*-
"""Phase 1 CRM analytics tools (read-only)."""

from __future__ import annotations

from datetime import timedelta
from typing import Any

from odoo import fields, _

from .base import BaseAITool
from .registry import register_tool
from .result import error_result, tool_result


def _require_crm(env):
    if 'crm.lead' not in env:
        return error_result(_('Install the CRM app to use this insight.'))
    return None


@register_tool
class FindCustomerTool(BaseAITool):
    name = 'find_customer'
    description = 'Search customers or find inactive customers.'

    def execute(self, arguments: dict[str, Any]) -> dict[str, Any]:
        limit = min(int(arguments.get('limit') or 20), 50)
        inactive_months = int(arguments.get('inactive_months') or 0)
        Partner = self.env['res.partner']
        Partner.check_access('read')
        domain = [('customer_rank', '>', 0)]
        if inactive_months:
            cutoff = fields.Date.today() - timedelta(days=inactive_months * 30)
            recent_partners = self.env['sale.order'].search([
                ('state', 'in', ('sale', 'done')),
                ('date_order', '>=', cutoff),
            ]).mapped('partner_id').ids
            domain += [('id', 'not in', recent_partners)]
            headline = f'Customers inactive for {inactive_months} months'
        else:
            query = (arguments.get('query') or '').strip()
            if query:
                domain += ['|', ('name', 'ilike', query), ('ref', 'ilike', query)]
            headline = 'Customer search results'
        partners = Partner.search(domain, limit=limit, order='name asc')
        return tool_result(
            headline=f'{len(partners)} customers found',
            summary=f'{headline}: {len(partners)} matches.',
            model='res.partner',
            domain=domain,
            record_ids=partners.ids,
            lines=[{'name': partner.name, 'email': partner.email} for partner in partners[:10]],
            category='crm' if inactive_months else 'sales',
        )


@register_tool
class TopOpportunitiesTool(BaseAITool):
    name = 'top_opportunities'
    description = 'List the highest value open CRM opportunities.'

    def execute(self, arguments: dict[str, Any]) -> dict[str, Any]:
        missing = _require_crm(self.env)
        if missing:
            return missing
        limit = min(int(arguments.get('limit') or 10), 20)
        Lead = self.env['crm.lead']
        Lead.check_access('read')
        leads = Lead.search([
            ('type', '=', 'opportunity'),
            ('probability', '>', 0),
            ('active', '=', True),
        ], limit=limit, order='expected_revenue desc')
        total = sum(leads.mapped('expected_revenue'))
        return tool_result(
            headline=f'{len(leads)} top opportunities',
            summary=f'{len(leads)} open opportunities worth {total:.2f} expected revenue.',
            model='crm.lead',
            domain=[('id', 'in', leads.ids)],
            record_ids=leads.ids,
            category='crm',
        )


@register_tool
class LostLeadsTool(BaseAITool):
    name = 'lost_leads'
    description = 'List recently lost CRM leads and opportunities.'

    def execute(self, arguments: dict[str, Any]) -> dict[str, Any]:
        missing = _require_crm(self.env)
        if missing:
            return missing
        limit = min(int(arguments.get('limit') or 20), 50)
        Lead = self.env['crm.lead']
        Lead.check_access('read')
        leads = Lead.search([
            ('active', '=', False),
            ('probability', '=', 0),
        ], limit=limit, order='write_date desc')
        return tool_result(
            headline=f'{len(leads)} lost leads',
            summary=f'{len(leads)} lost leads or opportunities in the archive.',
            model='crm.lead',
            domain=[('id', 'in', leads.ids)],
            record_ids=leads.ids,
            category='crm',
        )


@register_tool
class FollowupOverdueTool(BaseAITool):
    name = 'followup_overdue'
    description = 'List CRM records with overdue next activities.'

    def execute(self, arguments: dict[str, Any]) -> dict[str, Any]:
        missing = _require_crm(self.env)
        if missing:
            return missing
        limit = min(int(arguments.get('limit') or 20), 50)
        Lead = self.env['crm.lead']
        Lead.check_access('read')
        today = fields.Date.today()
        leads = Lead.search([
            ('activity_date_deadline', '<', today),
            ('activity_ids', '!=', False),
        ], limit=limit)
        return tool_result(
            headline=f'{len(leads)} overdue follow-ups',
            summary=f'{len(leads)} CRM records need follow-up.',
            model='crm.lead',
            domain=[('id', 'in', leads.ids)],
            record_ids=leads.ids,
            category='crm',
        )


@register_tool
class PipelineRevenueTool(BaseAITool):
    name = 'pipeline_revenue'
    description = 'Summarize expected revenue from the open CRM pipeline.'

    def execute(self, arguments: dict[str, Any]) -> dict[str, Any]:
        missing = _require_crm(self.env)
        if missing:
            return missing
        Lead = self.env['crm.lead']
        Lead.check_access('read')
        leads = Lead.search([
            ('type', '=', 'opportunity'),
            ('active', '=', True),
            ('probability', '>', 0),
        ])
        expected = sum(leads.mapped('expected_revenue'))
        currency = self.env.company.currency_id.name
        return tool_result(
            headline=f'Pipeline expected revenue: {expected:.2f} {currency}',
            summary=f'Open pipeline expected revenue is {expected:.2f} {currency} across {len(leads)} opportunities.',
            model='crm.lead',
            domain=[('id', 'in', leads.ids)],
            record_ids=leads.ids,
            metrics=[{'label': 'Expected revenue', 'value': f'{expected:.2f} {currency}'}],
            category='crm',
        )
