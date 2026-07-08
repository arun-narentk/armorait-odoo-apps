# -*- coding: utf-8 -*-
"""Face matching against enrolled embeddings."""

import logging

from odoo import models

_logger = logging.getLogger(__name__)


class RnHrRecognizerService(models.AbstractModel):
    """Match a probe embedding against company face database."""

    _name = 'rn.hr.recognizer.service'
    _description = 'Face Recognizer Service'

    def match(self, company_id, probe_vector, threshold):
        """Return best employee match under the company threshold."""
        # Phase 4: cosine similarity / L2 over encrypted embeddings in memory cache.
        _logger.debug(
            'match called company=%s dims=%s threshold=%s',
            company_id,
            len(probe_vector or []),
            threshold,
        )
        return {
            'ok': False,
            'employee_id': False,
            'face_id': False,
            'confidence': 0.0,
            'result': 'no_face',
            'error': 'Matcher pending (Phase 4).',
        }
