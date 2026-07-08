# -*- coding: utf-8 -*-
"""Customer portal booking entry points (Phase 4 expands UI)."""

from odoo import http
from odoo.http import request


class RnBookingPortalController(http.Controller):
    """Portal routes for my appointments."""

    @http.route(['/my/appointments'], type='http', auth='user', website=True)
    def portal_my_appointments(self, **kwargs):
        appointments = request.env['rn.booking.appointment'].search([
            ('partner_id', '=', request.env.user.partner_id.id),
        ], limit=50)
        values = {
            'appointments': appointments,
            'page_name': 'rn_booking_appointments',
        }
        return request.render('rn_booking_platform.portal_my_appointments', values)
