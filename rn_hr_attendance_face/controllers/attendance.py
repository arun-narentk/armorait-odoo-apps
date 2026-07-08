# -*- coding: utf-8 -*-
"""Attendance kiosk JSON RPC endpoints."""

import logging

from odoo import http
from odoo.http import request

_logger = logging.getLogger(__name__)


class RnHrFaceAttendanceController(http.Controller):
    """Public and user endpoints for the OWL face kiosk."""

    @http.route('/rn_face/recognize', type='json', auth='user')
    def recognize(self, image_b64=None, camera_id=False, device_fingerprint=None, geo=None, **kwargs):
        """Accept a webcam frame and run the recognition pipeline (Phase 4)."""
        _logger.info('recognize called camera=%s', camera_id)
        return {
            'ok': False,
            'message': 'Recognition engine pending (Phase 4).',
            'result': 'no_face',
        }

    @http.route('/rn_face/health', type='http', auth='public', methods=['GET'], csrf=False)
    def health(self):
        """Simple health endpoint for monitoring."""
        return request.make_json_response({'status': 'ok', 'module': 'rn_hr_attendance_face'})
