# -*- coding: utf-8 -*-
"""Camera capture abstraction."""

import logging
from typing import Any, Dict

from odoo import models

_logger = logging.getLogger(__name__)


class RnHrCameraService(models.AbstractModel):
    """Open, probe, and capture frames from registered cameras."""

    _name = 'rn.hr.camera.service'
    _description = 'Face Attendance Camera Service'

    def open_stream(self, camera):
        """Open a camera stream handle (Phase 8 fills RTSP/USB logic)."""
        camera.ensure_one()
        _logger.info('Open stream placeholder for camera %s', camera.name)
        return {'ok': False, 'error': 'Camera stream not implemented yet (Phase 8).'}

    def capture_frame(self, camera):
        """Capture one RGB frame for detection."""
        camera.ensure_one()
        return {'ok': False, 'frame': None, 'error': 'Capture pending (Phase 4/8).'}

    def health_check(self, camera):
        """Return FPS/status snapshot for dashboard and cron."""
        camera.ensure_one()
        return {'ok': False, 'status': camera.status, 'message': 'Health check pending (Phase 8).'}
