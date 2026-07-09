# -*- coding: utf-8 -*-
"""Phase 2 write tools: quotations and payment reminders."""

from __future__ import annotations

from datetime import timedelta
from typing import Any

from odoo import _, fields

from .base import BaseAITool
from .registry import register_tool
from .result import error_result, write_result


@register_tool
class CreateQuotationTool(BaseAITool):
    name = 'create_quotation'
    description = 'Create a draft sales quotation for a customer and product with quantity.'

    def get_parameters_schema(self) -> dict[str, Any]:
        return {
            'type': 'object',
            'properties': {
                'partner_name': {
                    'type': 'string',
                    'description': 'Customer or company name.',
                },
                'product_name': {
                    'type': 'string',
                    'description': 'Product name to quote.',
                },
                'quantity': {
                    'type': 'number',
                    'description': 'Quantity to quote.',
                },
            },
            'required': ['partner_name', 'product_name'],
        }

    def execute(self, arguments: dict[str, Any]) -> dict[str, Any]:
        partner_name = (arguments.get('partner_name') or '').strip()
        product_name = (arguments.get('product_name') or '').strip()
        quantity = float(arguments.get('quantity') or 1.0)
        if not partner_name or not product_name:
            return error_result(_('Customer name and product name are required to create a quotation.'))
        if quantity <= 0:
            return error_result(_('Quantity must be greater than zero.'))

        Partner = self.env['res.partner']
        Product = self.env['product.product']
        SaleOrder = self.env['sale.order']
        Partner.check_access('read')
        Product.check_access('read')
        SaleOrder.check_access('create')

        partner = Partner.search([
            ('name', 'ilike', partner_name),
            ('customer_rank', '>', 0),
        ], limit=1) or Partner.search([('name', 'ilike', partner_name)], limit=1)
        if not partner:
            return error_result(_('No customer found matching "%s".') % partner_name)

        product = Product.search([
            ('sale_ok', '=', True),
            ('name', 'ilike', product_name),
        ], limit=1)
        if not product:
            return error_result(_('No sellable product found matching "%s".') % product_name)

        order = SaleOrder.create({
            'partner_id': partner.id,
            'order_line': [(0, 0, {
                'product_id': product.id,
                'product_uom_qty': quantity,
            })],
        })
        currency = self.env.company.currency_id.name
        return write_result(
            headline=_('Quotation %s created') % order.name,
            summary=_(
                'Draft quotation %(order)s created for %(partner)s with %(qty)s x %(product)s '
                '(%(amount)s %(currency)s).'
            ) % {
                'order': order.name,
                'partner': partner.display_name,
                'qty': quantity,
                'product': product.display_name,
                'amount': f'{order.amount_total:.2f}',
                'currency': currency,
            },
            model='sale.order',
            record_ids=order.ids,
            category='sales',
            open_label=_('Open Quotation'),
        )


@register_tool
class SendPaymentRemindersTool(BaseAITool):
    name = 'send_payment_reminders'
    description = 'Send payment reminder emails for overdue customer invoices.'

    def get_parameters_schema(self) -> dict[str, Any]:
        return {
            'type': 'object',
            'properties': {
                'days_overdue': {
                    'type': 'integer',
                    'description': 'Minimum days past due date. Use 0 for any overdue invoice.',
                },
                'limit': {
                    'type': 'integer',
                    'description': 'Maximum number of reminder emails to send.',
                },
            },
        }

    def execute(self, arguments: dict[str, Any]) -> dict[str, Any]:
        days = int(arguments.get('days_overdue') if arguments.get('days_overdue') is not None else 0)
        limit = min(int(arguments.get('limit') or 10), 25)
        cutoff = fields.Date.today() - timedelta(days=days)

        Move = self.env['account.move']
        Mail = self.env['mail.mail']
        Move.check_access('read')
        Mail.check_access('create')

        invoices = Move.search([
            ('move_type', '=', 'out_invoice'),
            ('state', '=', 'posted'),
            ('payment_state', 'in', ('not_paid', 'partial')),
            ('invoice_date_due', '<=', cutoff),
        ], limit=limit, order='invoice_date_due asc')

        sent = 0
        skipped = 0
        for invoice in invoices:
            partner = invoice.partner_id
            if not partner.email:
                skipped += 1
                continue
            body = _(
                '<p>Dear %(partner)s,</p>'
                '<p>This is a friendly reminder that invoice <strong>%(invoice)s</strong> '
                'with amount <strong>%(amount)s</strong> is overdue.</p>'
                '<p>Please arrange payment at your earliest convenience.</p>'
                '<p>Thank you.</p>'
            ) % {
                'partner': partner.name,
                'invoice': invoice.name,
                'amount': f'{invoice.amount_residual:.2f} {invoice.currency_id.name}',
            }
            Mail.create({
                'subject': _('Payment reminder: %s') % invoice.name,
                'body_html': body,
                'email_to': partner.email,
                'auto_delete': True,
            }).send()
            sent += 1

        if not invoices:
            return write_result(
                headline=_('No overdue invoices found'),
                summary=_('There are no overdue customer invoices matching your request.'),
                model='account.move',
                record_ids=[],
                category='accounting',
            )

        summary = _('Sent %(sent)s payment reminder email(s).') % {'sent': sent}
        if skipped:
            summary += ' ' + _('Skipped %(skipped)s invoice(s) without customer email.') % {'skipped': skipped}

        return write_result(
            headline=_('%(sent)s reminder email(s) sent') % {'sent': sent},
            summary=summary,
            model='account.move',
            record_ids=invoices.ids,
            category='accounting',
            open_label=_('Open Invoices'),
        )
