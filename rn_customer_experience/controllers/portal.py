# -*- coding: utf-8 -*-
"""Customer-facing experience portal routes."""

import base64
import logging

from odoo import http
from odoo.exceptions import AccessError
from odoo.http import request

_logger = logging.getLogger(__name__)


class RnCustomerExperiencePortal(http.Controller):

    def _get_partner(self):
        return request.env.user.partner_id.commercial_partner_id

    def _get_config(self):
        return request.env['rn.customer.experience.config'].sudo().search([
            ('company_id', '=', request.env.company.id),
            ('active', '=', True),
        ], limit=1)

    def _portal_vals(self, page_title, **extra):
        partner = self._get_partner()
        config = self._get_config()
        vals = {
            'page_title': page_title,
            'partner': partner,
            'config': config,
            'portal_config': config.get_portal_values() if config else {},
        }
        vals.update(extra)
        return vals

    def _track(self, event_type, description=''):
        try:
            request.env['rn.customer.experience.analytics.service'].track_event(
                event_type,
                partner=self._get_partner(),
                description=description,
            )
        except Exception as exc:
            _logger.debug('Analytics track skipped: %s', exc)

    @http.route(['/my/experience', '/my/experience/home'], type='http', auth='user', website=True)
    def portal_home(self, **kwargs):
        partner = self._get_partner()
        dashboard = request.env['rn.customer.experience.dashboard.service'].get_partner_dashboard(partner)
        self._track('dashboard', 'Home dashboard')
        return request.render(
            'rn_customer_experience.portal_experience_home',
            self._portal_vals('My Experience', dashboard=dashboard),
        )

    @http.route('/my/experience/orders', type='http', auth='user', website=True)
    def portal_orders(self, **kwargs):
        partner = self._get_partner()
        dashboard = request.env['rn.customer.experience.dashboard.service'].get_partner_dashboard(partner)
        return request.render(
            'rn_customer_experience.portal_experience_orders',
            self._portal_vals('Orders', dashboard=dashboard),
        )

    @http.route('/my/experience/invoices', type='http', auth='user', website=True)
    def portal_invoices(self, **kwargs):
        partner = self._get_partner()
        dashboard = request.env['rn.customer.experience.dashboard.service'].get_partner_dashboard(partner)
        self._track('invoice_view', 'Invoice list')
        return request.render(
            'rn_customer_experience.portal_experience_invoices',
            self._portal_vals('Invoices', dashboard=dashboard),
        )

    @http.route('/my/experience/downloads', type='http', auth='user', website=True)
    def portal_downloads(self, **kwargs):
        partner = self._get_partner()
        dashboard = request.env['rn.customer.experience.dashboard.service'].get_partner_dashboard(partner)
        return request.render(
            'rn_customer_experience.portal_experience_downloads',
            self._portal_vals('Downloads', dashboard=dashboard),
        )

    @http.route('/my/experience/download/<int:download_id>', type='http', auth='user', website=True)
    def portal_download_file(self, download_id, **kwargs):
        partner = self._get_partner()
        download = request.env['rn.customer.experience.download'].sudo().browse(download_id)
        if not download.exists():
            return request.not_found()
        if download.partner_id and download.partner_id.commercial_partner_id != partner:
            raise AccessError('You cannot access this file.')
        self._track('download', download.name)
        attachment = download.attachment_id.sudo()
        return request.make_response(
            base64.b64decode(attachment.datas),
            headers=[
                ('Content-Type', attachment.mimetype or 'application/octet-stream'),
                ('Content-Disposition', f'attachment; filename="{attachment.name}"'),
            ],
        )

    @http.route('/my/experience/tickets', type='http', auth='user', website=True)
    def portal_tickets(self, **kwargs):
        partner = self._get_partner()
        dashboard = request.env['rn.customer.experience.dashboard.service'].get_partner_dashboard(partner)
        return request.render(
            'rn_customer_experience.portal_experience_tickets',
            self._portal_vals('Support Tickets', dashboard=dashboard),
        )

    @http.route('/my/experience/tickets/new', type='http', auth='user', website=True, methods=['GET', 'POST'])
    def portal_ticket_new(self, **post):
        partner = self._get_partner()
        if request.httprequest.method == 'POST':
            ticket = request.env['rn.customer.experience.ticket'].sudo().create({
                'name': post.get('name'),
                'partner_id': partner.id,
                'description': post.get('description'),
                'category': post.get('category') or 'service',
            })
            ai = request.env['rn.customer.experience.assistant.service']
            suggestion = ai.answer_query(partner, post.get('description', ''))
            ticket.write({
                'ai_category': ticket.category,
                'ai_suggestion': suggestion.get('answer'),
            })
            self._track('ticket_create', ticket.reference)
            return request.redirect('/my/experience/tickets')
        return request.render(
            'rn_customer_experience.portal_experience_ticket_form',
            self._portal_vals('New Ticket'),
        )

    @http.route('/my/experience/warranty', type='http', auth='user', website=True)
    def portal_warranty(self, **kwargs):
        partner = self._get_partner()
        dashboard = request.env['rn.customer.experience.dashboard.service'].get_partner_dashboard(partner)
        return request.render(
            'rn_customer_experience.portal_experience_warranty',
            self._portal_vals('Warranty', dashboard=dashboard),
        )

    @http.route('/my/experience/amc', type='http', auth='user', website=True)
    def portal_amc(self, **kwargs):
        partner = self._get_partner()
        dashboard = request.env['rn.customer.experience.dashboard.service'].get_partner_dashboard(partner)
        return request.render(
            'rn_customer_experience.portal_experience_amc',
            self._portal_vals('AMC Contracts', dashboard=dashboard),
        )

    @http.route('/my/experience/assistant', type='jsonrpc', auth='user', website=True)
    def portal_assistant(self, query):
        partner = self._get_partner()
        self._track('ai_query', query[:120])
        return request.env['rn.customer.experience.assistant.service'].answer_query(partner, query)
