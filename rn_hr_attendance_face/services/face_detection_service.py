# -*- coding: utf-8 -*-
"""Face detection service (OpenCV / InsightFace / ONNX)."""

import logging

from odoo import models

_logger = logging.getLogger(__name__)


class RnHrFaceDetectionService(models.AbstractModel):
    """Detect face bounding boxes in a frame."""

    _name = 'rn.hr.face.detection.service'
    _description = 'Face Detection Service'

    def detect_faces(self, frame_bytes, model='opencv'):
        """Return face boxes for the given image bytes."""
        # Phase 4: plug OpenCV/InsightFace detectors behind this interface.
        _logger.debug('detect_faces called with model=%s', model)
        return {
            'ok': False,
            'faces': [],
            'count': 0,
            'error': 'Detector not implemented yet (Phase 4).',
        }
