# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import logging
import re
from odoo import api, fields, models, _

_logger = logging.getLogger(__name__)

SIMILARITY_THRESHOLD = 0.5  # 0-1; pairs above this are stored


class HrResumeSimilarity(models.Model):
    _name = 'hr.resume.similarity'
    _description = 'Resume similarity pair'
    _order = 'similarity_score desc'

    applicant_id = fields.Many2one('hr.applicant', string='Applicant', required=True, ondelete='cascade')
    other_applicant_id = fields.Many2one('hr.applicant', string='Similar to', required=True, ondelete='cascade')
    similarity_score = fields.Float(string='Similarity', help='0-1 score (e.g. Jaccard on words).')

    _sql_constraints = [
        ('unique_pair', 'unique(applicant_id, other_applicant_id)', 'Similarity pair already exists.'),
    ]

    @api.model
    def _cron_compute_similarities(self, limit=50):
        """Compute similarity pairs for applicants with resume_text. Run periodically."""
        applicants = self.env['hr.applicant'].search([
            ('resume_text', '!=', False),
            ('resume_text', '!=', ''),
            ('parsing_status', '=', 'done'),
        ], limit=limit, order='id desc')
        self._compute_similarities_for_applicants(applicants)

    @api.model
    def _compute_similarities_for_applicants(self, applicants):
        for applicant in applicants:
            try:
                applicant._compute_resume_similarities()
            except Exception as e:
                _logger.exception("Similarity compute failed for applicant %s: %s", applicant.id, e)


def _jaccard_similarity(text1, text2):
    """Return Jaccard similarity (0-1) based on word sets. Simple and fast."""
    if not text1 or not text2:
        return 0.0
    words1 = set(_normalize_text(text1).split())
    words2 = set(_normalize_text(text2).split())
    if not words1 or not words2:
        return 0.0
    inter = len(words1 & words2)
    union = len(words1 | words2)
    return inter / union if union else 0.0


def _normalize_text(text):
    text = (text or '').lower()
    text = re.sub(r'[^\w\s]', ' ', text)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()
