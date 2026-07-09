# -*- coding: utf-8 -*-
"""Gather Odoo business context for email generation."""

import logging
from datetime import date

from odoo import fields, models

_logger = logging.getLogger(__name__)


class RnAiEmailContextService(models.AbstractModel):
    _name = 'rn.ai.email.context.service'
    _description = 'AI Email Context Service'

    def build_context(self, partner=None, res_model=None, res_id=None, company_id=None):
        company_id = company_id or self.env.company.id
        ctx = {
            'partner_name': partner.name if partner else '',
            'partner_email': partner.email if partner else '',
            'company_name': self.env.company.name,
            'salesperson': self.env.user.name,
            'today': str(fields.Date.context_today(self)),
        }
        if res_model == 'sale.order' and res_id:
            ctx.update(self._sale_context(res_id))
        elif res_model == 'account.move' and res_id:
            ctx.update(self._invoice_context(res_id))
        elif res_model == 'crm.lead' and res_id:
            ctx.update(self._lead_context(res_id))
        elif partner:
            ctx.update(self._partner_context(partner))
        return ctx

    def context_to_text(self, ctx):
        lines = [f'{k}: {v}' for k, v in ctx.items() if v]
        return '\n'.join(lines)

    def _sale_context(self, res_id):
        order = self.env['sale.order'].browse(res_id)
        if not order.exists():
            return {}
        return {
            'quotation': order.name,
            'amount_total': order.amount_total,
            'currency': order.currency_id.name,
            'order_state': order.state,
            'products': ', '.join(order.order_line.mapped('product_id.display_name')[:5]),
        }

    def _invoice_context(self, res_id):
        move = self.env['account.move'].browse(res_id)
        if not move.exists():
            return {}
        overdue_days = 0
        if move.invoice_date_due and move.invoice_date_due < date.today():
            overdue_days = (date.today() - move.invoice_date_due).days
        return {
            'invoice': move.name,
            'invoice_ref': move.ref or '',
            'amount_due': move.amount_residual,
            'due_date': str(move.invoice_date_due) if move.invoice_date_due else '',
            'overdue_days': overdue_days,
            'payment_state': move.payment_state,
        }

    def _lead_context(self, res_id):
        lead = self.env['crm.lead'].browse(res_id)
        if not lead.exists():
            return {}
        return {
            'lead': lead.name,
            'stage': lead.stage_id.name if lead.stage_id else '',
            'expected_revenue': lead.expected_revenue,
        }

    def _partner_context(self, partner):
        orders = self.env['sale.order'].search([
            ('partner_id', '=', partner.id),
            ('state', 'in', ('sale', 'done')),
        ], limit=3, order='date_order desc')
        invoices = self.env['account.move'].search([
            ('partner_id', '=', partner.id),
            ('move_type', '=', 'out_invoice'),
            ('payment_state', 'in', ('not_paid', 'partial')),
        ], limit=3)
        return {
            'recent_orders': ', '.join(orders.mapped('name')),
            'open_invoices': ', '.join(invoices.mapped('name')),
            'open_invoice_amount': sum(invoices.mapped('amount_residual')),
        }
