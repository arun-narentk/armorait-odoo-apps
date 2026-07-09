# -*- coding: utf-8 -*-
"""Smart activity recommendations."""

import logging

from odoo import models

_logger = logging.getLogger(__name__)


class RnCrmActivityService(models.AbstractModel):
    """Suggest next best activities for a lead."""

    _name = 'rn.crm.activity.service'
    _description = 'CRM Activity Service'

    def recommend(self, lead):
        """Return ordered activity template suggestions."""
        lead.ensure_one()
        templates = self.env['rn.crm.activity.template'].search([('active', '=', True)])
        _logger.debug('Recommend activities for lead %s count=%s', lead.id, len(templates))
        return templates
