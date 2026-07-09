# -*- coding: utf-8 -*-
"""Face embedding generation and encryption helpers."""

import base64
import logging

from odoo import models

_logger = logging.getLogger(__name__)


class RnHrEmbeddingService(models.AbstractModel):
    """Create and encrypt face embedding vectors for storage."""

    _name = 'rn.hr.embedding.service'
    _description = 'Face Embedding Service'

    def generate_embedding(self, face_crops, model='insightface'):
        """Generate an averaged embedding from multiple face crops."""
        # Phase 3: InsightFace / FaceNet / ONNX produce 128/512-d vectors.
        _logger.info('generate_embedding placeholder model=%s crops=%s', model, len(face_crops or []))
        return {
            'ok': False,
            'vector': None,
            'version': '%s-pending' % model,
            'error': 'Embedding engine pending (Phase 3).',
        }

    def encrypt_embedding(self, vector):
        """Encode embedding for DB storage (Phase 3 adds Fernet encryption)."""
        raw = ','.join(str(x) for x in (vector or []))
        token = base64.b64encode(raw.encode('utf-8')).decode('ascii')
        return token

    def decrypt_embedding(self, token):
        """Decode stored embedding back to float list."""
        if not token:
            return []
        try:
            raw = base64.b64decode(token.encode('ascii')).decode('utf-8')
            return [float(x) for x in raw.split(',') if x]
        except Exception:
            _logger.exception('Failed to decrypt embedding')
            return []
