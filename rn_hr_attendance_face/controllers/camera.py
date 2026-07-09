# -*- coding: utf-8 -*-
"""Camera status HTTP endpoints."""

from odoo import http
from odoo.http import request


class RnHrFaceCameraController(http.Controller):
    """Expose camera status for kiosk and monitoring."""

    @http.route('/rn_face/camera/<int:camera_id>/status', type='json', auth='user')
    def camera_status(self, camera_id, **kwargs):
        """Return status of one camera device."""
        camera = request.env['rn.hr.camera.device'].browse(camera_id).exists()
        if not camera:
            return {'ok': False, 'error': 'Camera not found'}
        return request.env['rn.hr.camera.service'].health_check(camera)
