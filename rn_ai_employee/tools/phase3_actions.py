# -*- coding: utf-8 -*-
"""Phase 3 write skills: RFQ, activities, partner email, PO approval, stock reserve."""

from __future__ import annotations

from datetime import timedelta
from typing import Any

from odoo import _, fields

from .base import BaseAITool
from .registry import register_tool
from .result import error_result, tool_result, write_result


def _partner_ids_from_records(env, res_model: str, record_ids: list[int]) -> list[int]:
    if not record_ids or not res_model:
        return []
    records = env[res_model].browse(record_ids).exists()
    if res_model == 'res.partner':
        return records.ids
    if res_model == 'sale.order':
        return records.mapped('partner_id').ids
    if res_model == 'account.move':
        return records.mapped('partner_id').ids
    if res_model == 'crm.lead':
        return records.mapped('partner_id').filtered(lambda p: p).ids
    partner_field = records._fields.get('partner_id')
    if partner_field:
        return records.mapped('partner_id').ids
    return []


@register_tool
class MorningBriefingTool(BaseAITool):
    name = 'morning_briefing'
    description = 'Generate an executive morning briefing with revenue, collections, and suggested actions.'

    def execute(self, arguments: dict[str, Any]) -> dict[str, Any]:
        briefing = self.env['rn.ai.employee.service'].generate_morning_briefing()
        return tool_result(
            headline=_('Your morning briefing'),
            summary=briefing,
            category='executive',
        )


@register_tool
class CreateRfqTool(BaseAITool):
    name = 'create_rfq'
    description = 'Create a draft purchase RFQ for a vendor and product.'
    is_write_tool = True
    requires_confirmation = True

    def get_parameters_schema(self) -> dict[str, Any]:
        return {
            'type': 'object',
            'properties': {
                'vendor_name': {'type': 'string', 'description': 'Vendor name.'},
                'product_name': {'type': 'string', 'description': 'Product to purchase.'},
                'quantity': {'type': 'number', 'description': 'Quantity to request.'},
            },
            'required': ['vendor_name', 'product_name'],
        }

    def execute(self, arguments: dict[str, Any]) -> dict[str, Any]:
        vendor_name = (arguments.get('vendor_name') or '').strip()
        product_name = (arguments.get('product_name') or '').strip()
        quantity = float(arguments.get('quantity') or 1.0)
        if not vendor_name or not product_name:
            return error_result(_('Vendor name and product name are required to create an RFQ.'))
        if quantity <= 0:
            return error_result(_('Quantity must be greater than zero.'))

        Partner = self.env['res.partner']
        Product = self.env['product.product']
        PurchaseOrder = self.env['purchase.order']
        Partner.check_access('read')
        Product.check_access('read')
        PurchaseOrder.check_access('create')

        vendor = Partner.search([
            ('name', 'ilike', vendor_name),
            ('supplier_rank', '>', 0),
        ], limit=1) or Partner.search([('name', 'ilike', vendor_name)], limit=1)
        if not vendor:
            return error_result(_('No vendor found matching "%s".') % vendor_name)

        product = Product.search([
            ('purchase_ok', '=', True),
            ('name', 'ilike', product_name),
        ], limit=1)
        if not product:
            return error_result(_('No purchasable product found matching "%s".') % product_name)

        order = PurchaseOrder.create({
            'partner_id': vendor.id,
            'order_line': [(0, 0, {
                'product_id': product.id,
                'product_qty': quantity,
            })],
        })
        currency = self.env.company.currency_id.name
        return write_result(
            headline=_('RFQ %s created') % order.name,
            summary=_(
                'Draft RFQ %(order)s created for %(vendor)s with %(qty)s x %(product)s '
                '(%(amount)s %(currency)s).'
            ) % {
                'order': order.name,
                'vendor': vendor.display_name,
                'qty': quantity,
                'product': product.display_name,
                'amount': f'{order.amount_total:.2f}',
                'currency': currency,
            },
            model='purchase.order',
            record_ids=order.ids,
            category='purchase',
            open_label=_('Open RFQ'),
        )


@register_tool
class ScheduleActivityTool(BaseAITool):
    name = 'schedule_activity'
    description = 'Schedule a follow-up activity on one or more business records.'
    is_write_tool = True
    requires_confirmation = True

    def get_parameters_schema(self) -> dict[str, Any]:
        return {
            'type': 'object',
            'properties': {
                'res_model': {'type': 'string'},
                'record_ids': {'type': 'array', 'items': {'type': 'integer'}},
                'summary': {'type': 'string', 'description': 'Activity summary text.'},
                'days_ahead': {'type': 'integer', 'description': 'Due date offset in days.'},
            },
        }

    def execute(self, arguments: dict[str, Any]) -> dict[str, Any]:
        res_model = (arguments.get('res_model') or '').strip()
        record_ids = list(arguments.get('record_ids') or [])
        summary = (arguments.get('summary') or _('AI Copilot follow-up')).strip()
        days_ahead = int(arguments.get('days_ahead') or 1)
        if not res_model or not record_ids:
            return error_result(_('A record model and at least one record id are required.'))
        if res_model not in self.env:
            return error_result(_('Model "%s" is not available.') % res_model)

        Activity = self.env['mail.activity']
        ActivityType = self.env['mail.activity.type']
        Activity.check_access('create')
        records = self.env[res_model].browse(record_ids).exists()
        if not records:
            return error_result(_('No records found to schedule activities on.'))

        activity_type = ActivityType.search([('category', '=', 'default')], limit=1)
        if not activity_type:
            activity_type = ActivityType.search([], limit=1)
        if not activity_type:
            return error_result(_('No activity type is configured in Odoo.'))

        due = fields.Date.today() + timedelta(days=max(days_ahead, 0))
        created_ids = []
        model_id = self.env['ir.model']._get(res_model).id
        for record in records[:10]:
            activity = Activity.create({
                'activity_type_id': activity_type.id,
                'res_model_id': model_id,
                'res_id': record.id,
                'summary': summary,
                'date_deadline': due,
                'user_id': self.env.user.id,
            })
            created_ids.append(activity.id)

        return write_result(
            headline=_('%(count)s activity(ies) scheduled') % {'count': len(created_ids)},
            summary=_('Follow-up activities scheduled for %(count)s record(s), due on %(due)s.') % {
                'count': len(created_ids),
                'due': due,
            },
            model='mail.activity',
            record_ids=created_ids,
            category='crm',
            open_label=_('Open Activities'),
        )


@register_tool
class SendPartnerEmailTool(BaseAITool):
    name = 'send_partner_email'
    description = 'Send a short email to customers or partners linked to recent records.'
    is_write_tool = True
    requires_confirmation = True

    def get_parameters_schema(self) -> dict[str, Any]:
        return {
            'type': 'object',
            'properties': {
                'res_model': {'type': 'string'},
                'record_ids': {'type': 'array', 'items': {'type': 'integer'}},
                'subject': {'type': 'string'},
                'body': {'type': 'string'},
            },
        }

    def execute(self, arguments: dict[str, Any]) -> dict[str, Any]:
        res_model = (arguments.get('res_model') or '').strip()
        record_ids = list(arguments.get('record_ids') or [])
        subject = (arguments.get('subject') or _('Message from your account team')).strip()
        body_text = (arguments.get('body') or _('Hello, we are following up on your recent business with us.')).strip()

        partner_ids = list(arguments.get('partner_ids') or [])
        if not partner_ids and res_model and record_ids:
            partner_ids = _partner_ids_from_records(self.env, res_model, record_ids)
        if not partner_ids:
            return error_result(_('No customer or partner records were found to email.'))

        Mail = self.env['mail.mail']
        Partner = self.env['res.partner']
        Mail.check_access('create')
        Partner.check_access('read')
        partners = Partner.browse(partner_ids).exists().filtered('email')
        if not partners:
            return error_result(_('No partners with an email address were found.'))

        sent = 0
        for partner in partners[:25]:
            Mail.create({
                'subject': subject,
                'body_html': f'<p>{body_text}</p>',
                'email_to': partner.email,
                'auto_delete': True,
            }).send()
            sent += 1

        return write_result(
            headline=_('%(sent)s email(s) sent') % {'sent': sent},
            summary=_('Sent %(sent)s follow-up email(s) to customers or partners.') % {'sent': sent},
            model='res.partner',
            record_ids=partners.ids,
            category='sales',
            open_label=_('Open Partners'),
        )


@register_tool
class ConfirmPurchaseOrderTool(BaseAITool):
    name = 'confirm_purchase_order'
    description = 'Confirm a draft purchase order by reference or vendor name.'
    is_write_tool = True
    requires_confirmation = True

    def get_parameters_schema(self) -> dict[str, Any]:
        return {
            'type': 'object',
            'properties': {
                'order_reference': {'type': 'string', 'description': 'PO name or reference.'},
                'vendor_name': {'type': 'string', 'description': 'Vendor name if reference is missing.'},
            },
        }

    def execute(self, arguments: dict[str, Any]) -> dict[str, Any]:
        reference = (arguments.get('order_reference') or '').strip()
        vendor_name = (arguments.get('vendor_name') or '').strip()
        PurchaseOrder = self.env['purchase.order']
        PurchaseOrder.check_access('write')

        domain = [('state', '=', 'draft')]
        if reference:
            domain.append(('name', 'ilike', reference))
        elif vendor_name:
            domain.append(('partner_id.name', 'ilike', vendor_name))
        else:
            return error_result(_('Provide a purchase order reference or vendor name.'))

        order = PurchaseOrder.search(domain, limit=1, order='date_order desc')
        if not order:
            return error_result(_('No draft purchase order matched your request.'))

        order.button_confirm()
        return write_result(
            headline=_('Purchase order %s confirmed') % order.name,
            summary=_('Purchase order %(order)s for %(vendor)s was confirmed.') % {
                'order': order.name,
                'vendor': order.partner_id.display_name,
            },
            model='purchase.order',
            record_ids=order.ids,
            category='purchase',
            open_label=_('Open Purchase Order'),
        )


@register_tool
class ReserveStockTool(BaseAITool):
    name = 'reserve_stock'
    description = 'Reserve available stock for a product in the default warehouse.'
    is_write_tool = True
    requires_confirmation = True

    def get_parameters_schema(self) -> dict[str, Any]:
        return {
            'type': 'object',
            'properties': {
                'product_name': {'type': 'string'},
                'quantity': {'type': 'number'},
            },
            'required': ['product_name'],
        }

    def execute(self, arguments: dict[str, Any]) -> dict[str, Any]:
        product_name = (arguments.get('product_name') or '').strip()
        quantity = float(arguments.get('quantity') or 1.0)
        if not product_name:
            return error_result(_('Product name is required to reserve stock.'))
        if quantity <= 0:
            return error_result(_('Quantity must be greater than zero.'))

        Product = self.env['product.product']
        Quant = self.env['stock.quant']
        Product.check_access('read')
        Quant.check_access('write')

        product = Product.search([
            ('type', '=', 'product'),
            ('name', 'ilike', product_name),
        ], limit=1)
        if not product:
            return error_result(_('No storable product found matching "%s".') % product_name)

        warehouse = self.env.company.warehouse_id
        if not warehouse:
            return error_result(_('No default warehouse is configured for this company.'))

        location = warehouse.lot_stock_id
        quant = Quant.search([
            ('product_id', '=', product.id),
            ('location_id', '=', location.id),
        ], limit=1)
        if not quant:
            return error_result(_('No stock quant found for %(product)s in %(location)s.') % {
                'product': product.display_name,
                'location': location.display_name,
            })

        available = quant.quantity - quant.reserved_quantity
        reserve_qty = min(quantity, max(available, 0))
        if reserve_qty <= 0:
            return error_result(_('No available quantity to reserve for %s.') % product.display_name)

        quant.reserved_quantity += reserve_qty
        return write_result(
            headline=_('Reserved %(qty)s %(product)s') % {'qty': reserve_qty, 'product': product.display_name},
            summary=_(
                'Reserved %(qty)s units of %(product)s in %(location)s. '
                'Available before reserve: %(available)s.'
            ) % {
                'qty': reserve_qty,
                'product': product.display_name,
                'location': location.display_name,
                'available': available,
            },
            model='stock.quant',
            record_ids=quant.ids,
            category='inventory',
            open_label=_('Open Stock'),
        )
