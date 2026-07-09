# -*- coding: utf-8 -*-
"""REST-style API stubs for booking platform."""

from odoo import http
from odoo.http import request


class RnBookingApiController(http.Controller):
    """API for appointments, slots, and health."""

    @http.route('/api/rn_booking/v1/dashboard', type='json', auth='user')
    def api_dashboard(self, **kwargs):
        return {'ok': True, 'data': request.env['rn.booking.dashboard.service'].get_dashboard_data()}

    @http.route('/api/rn_booking/v1/slots', type='json', auth='user')
    def api_slots(self, service_id=None, staff_id=None, day=None, **kwargs):
        service = request.env['rn.booking.service'].browse(service_id)
        if not service.exists():
            return {'ok': False, 'error': 'Service not found'}
        staff = request.env['rn.booking.staff'].browse(staff_id) if staff_id else None
        slots = request.env['rn.booking.availability.service'].get_slots(
            service, staff=staff if staff and staff.exists() else None, day=day
        )
        return {'ok': True, 'slots': slots}

    @http.route('/rn_booking_platform/health', type='http', auth='public', methods=['GET'], csrf=False)
    def health(self):
        return request.make_json_response({'status': 'ok', 'module': 'rn_booking_platform'})
