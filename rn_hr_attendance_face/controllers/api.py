# -*- coding: utf-8 -*-
"""REST-style API stubs for external integrations."""

from odoo import http
from odoo.http import request


class RnHrFaceApiController(http.Controller):
    """REST API placeholders (Phase 10 expands auth and payloads)."""

    @http.route('/api/rn_face/v1/attendance', type='json', auth='user', methods=['POST'])
    def api_attendance(self, **payload):
        """Create attendance from an external recognition result."""
        return {'ok': False, 'error': 'API pending (Phase 10).'}

    @http.route('/api/rn_face/v1/register', type='json', auth='user', methods=['POST'])
    def api_register(self, **payload):
        """Register an employee face embedding via API."""
        return {'ok': False, 'error': 'API pending (Phase 10).'}

    @http.route('/api/rn_face/v1/camera_status', type='json', auth='user', methods=['GET'])
    def api_camera_status(self, **kwargs):
        """List camera statuses for the company."""
        cameras = request.env['rn.hr.camera.device'].search([])
        return {
            'ok': True,
            'cameras': [{
                'id': c.id,
                'name': c.name,
                'status': c.status,
            } for c in cameras],
        }
