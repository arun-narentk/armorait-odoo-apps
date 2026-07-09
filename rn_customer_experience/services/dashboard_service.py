# -*- coding: utf-8 -*-
"""Aggregate customer portal dashboard data from Odoo records."""

from odoo import fields, models


class RnCustomerExperienceDashboardService(models.AbstractModel):
    _name = 'rn.customer.experience.dashboard.service'
    _description = 'Customer Experience Dashboard Service'

    def get_partner_dashboard(self, partner, company=None):
        company = company or self.env.company
        commercial = partner.commercial_partner_id
        orders = self.env['sale.order'].sudo().search([
            ('partner_id', 'child_of', commercial.id),
            ('company_id', '=', company.id),
        ], order='date_order desc', limit=8)
        quotations = orders.filtered(lambda o: o.state in ('draft', 'sent'))
        confirmed_orders = orders.filtered(lambda o: o.state in ('sale', 'done'))
        invoices = self.env['account.move'].sudo().search([
            ('partner_id', 'child_of', commercial.id),
            ('company_id', '=', company.id),
            ('move_type', 'in', ('out_invoice', 'out_refund')),
            ('state', '=', 'posted'),
        ], order='invoice_date desc', limit=8)
        outstanding = invoices.filtered(lambda inv: inv.payment_state in ('not_paid', 'partial'))
        deliveries = []
        if 'stock.picking' in self.env:
            deliveries = self.env['stock.picking'].sudo().search([
                ('partner_id', 'child_of', commercial.id),
                ('company_id', '=', company.id),
                ('picking_type_code', '=', 'outgoing'),
            ], order='scheduled_date desc', limit=8)
        downloads = self.env['rn.customer.experience.download'].sudo().search([
            ('company_id', '=', company.id),
            '|', ('partner_id', '=', commercial.id), ('is_public', '=', True),
        ], limit=20)
        tickets = self.env['rn.customer.experience.ticket'].sudo().search([
            ('partner_id', 'child_of', commercial.id),
            ('company_id', '=', company.id),
        ], order='create_date desc', limit=5)
        warranties = self.env['rn.customer.experience.warranty'].sudo().search([
            ('partner_id', 'child_of', commercial.id),
            ('company_id', '=', company.id),
            ('state', '=', 'active'),
        ], limit=5)
        amcs = self.env['rn.customer.experience.amc'].sudo().search([
            ('partner_id', 'child_of', commercial.id),
            ('company_id', '=', company.id),
        ], order='renewal_date', limit=5)
        return {
            'summary': {
                'outstanding_invoices': len(outstanding),
                'outstanding_amount': sum(outstanding.mapped('amount_residual')),
                'open_orders': len(confirmed_orders.filtered(
                    lambda o: getattr(o, 'delivery_status', 'full') != 'full'
                )),
                'open_quotations': len(quotations),
                'open_tickets': len(tickets.filtered(lambda t: t.state not in ('resolved', 'closed'))),
                'active_warranties': len(warranties),
                'active_amcs': len(amcs.filtered(lambda a: a.state == 'active')),
            },
            'orders': self._serialize_orders(confirmed_orders),
            'quotations': self._serialize_orders(quotations),
            'invoices': self._serialize_invoices(invoices),
            'outstanding_invoices': self._serialize_invoices(outstanding),
            'deliveries': self._serialize_deliveries(deliveries),
            'downloads': self._serialize_downloads(downloads),
            'tickets': self._serialize_tickets(tickets),
            'warranties': self._serialize_warranties(warranties),
            'amcs': self._serialize_amcs(amcs),
            'notifications': self._build_notifications(outstanding, deliveries, amcs),
        }

    def _serialize_orders(self, orders):
        return [{
            'id': order.id,
            'name': order.name,
            'date': fields.Date.to_string(order.date_order.date()) if order.date_order else '',
            'amount_total': order.amount_total,
            'state': order.state,
            'delivery_status': getattr(order, 'delivery_status', False),
        } for order in orders]

    def _serialize_invoices(self, invoices):
        return [{
            'id': inv.id,
            'name': inv.name,
            'invoice_date': fields.Date.to_string(inv.invoice_date) if inv.invoice_date else '',
            'amount_total': inv.amount_total,
            'amount_residual': inv.amount_residual,
            'payment_state': inv.payment_state,
            'portal_url': f'/my/invoices/{inv.id}',
        } for inv in invoices]

    def _serialize_deliveries(self, pickings):
        if not pickings:
            return []
        return [{
            'id': picking.id,
            'name': picking.name,
            'scheduled_date': fields.Datetime.to_string(picking.scheduled_date) if picking.scheduled_date else '',
            'state': picking.state,
        } for picking in pickings]

    def _serialize_downloads(self, downloads):
        return [{
            'id': dl.id,
            'name': dl.name,
            'document_type': dl.document_type,
            'url': f'/my/experience/download/{dl.id}',
        } for dl in downloads]

    def _serialize_tickets(self, tickets):
        return [{
            'id': ticket.id,
            'reference': ticket.reference,
            'name': ticket.name,
            'state': ticket.state,
            'category': ticket.category,
        } for ticket in tickets]

    def _serialize_warranties(self, warranties):
        return [{
            'id': war.id,
            'name': war.name,
            'product': war.product_id.display_name if war.product_id else '',
            'end_date': fields.Date.to_string(war.end_date) if war.end_date else '',
            'state': war.state,
        } for war in warranties]

    def _serialize_amcs(self, amcs):
        return [{
            'id': amc.id,
            'name': amc.name,
            'renewal_date': fields.Date.to_string(amc.renewal_date) if amc.renewal_date else '',
            'next_visit_date': fields.Date.to_string(amc.next_visit_date) if amc.next_visit_date else '',
            'state': amc.state,
        } for amc in amcs]

    def _build_notifications(self, outstanding, deliveries, amcs):
        notes = []
        if outstanding:
            notes.append({
                'level': 'warning',
                'message': f'You have {len(outstanding)} outstanding invoice(s).',
            })
        if deliveries:
            notes.append({
                'level': 'info',
                'message': f'{len(deliveries)} recent delivery update(s) available.',
            })
        expiring = amcs.filtered(lambda a: a.state == 'expiring')
        if expiring:
            notes.append({
                'level': 'warning',
                'message': f'{len(expiring)} AMC contract(s) are due for renewal.',
            })
        return notes
