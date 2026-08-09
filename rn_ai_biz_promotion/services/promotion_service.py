# -*- coding: utf-8 -*-

import logging

from odoo import models

_logger = logging.getLogger(__name__)


class AiBizPromotionService(models.AbstractModel):
    """Service helpers for website promotion rendering."""

    _name = 'ai.biz.promotion.service'
    _description = 'AI BIZ Promotion Service'

    def get_active_promotion(self):
        """Return the first active promotion ordered by sequence."""
        promotion = self.env['ai.biz.promotion'].sudo().search(
            [('active', '=', True)],
            order='sequence, id',
            limit=1,
        )
        if not promotion:
            _logger.debug('No active AI BIZ promotion found for /ai-biz')
        return promotion
