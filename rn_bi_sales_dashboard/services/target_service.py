# -*- coding: utf-8 -*-
"""Sales target lookups."""

import logging

from odoo import fields, models

_logger = logging.getLogger(__name__)


class RnBiTargetService(models.AbstractModel):
    """Resolve the most relevant open target for a company."""

    _name = 'rn.bi.target.service'
    _description = 'BI Target Service'

    def get_current_target(self, company_id=None):
        """Return open target covering today, or empty defaults."""
        company_id = company_id or self.env.company.id
        today = fields.Date.context_today(self)
        target = self.env['rn.bi.sales.target'].search([
            ('company_id', '=', company_id),
            ('state', '=', 'open'),
            ('date_start', '<=', today),
            ('date_end', '>=', today),
        ], limit=1)
        if not target:
            return {'target_amount': 0.0, 'achievement_pct': 0.0, 'remaining_amount': 0.0}
        return {
            'id': target.id,
            'name': target.name,
            'target_amount': target.target_amount,
            'achieved_amount': target.achieved_amount,
            'achievement_pct': target.achievement_pct,
            'remaining_amount': target.remaining_amount,
        }
