# -*- coding: utf-8 -*-
"""Lead merge orchestration."""

import logging

from odoo import models

_logger = logging.getLogger(__name__)


class RnCrmMergeService(models.AbstractModel):
    """Merge secondary leads into a master lead with audit logging."""

    _name = 'rn.crm.merge.service'
    _description = 'CRM Merge Service'

    def merge_leads(self, master, others, preserve=None):
        """Merge others into master (Phase 5 completes chatter/attachment move)."""
        master.ensure_one()
        preserve = preserve or {}
        ids = ','.join(str(i) for i in others.ids)
        log = self.env['rn.crm.merge.log'].create({
            'name': 'Merge into %s' % master.display_name,
            'master_lead_id': master.id,
            'merged_lead_ids': ids,
            'preserve_chatter': preserve.get('chatter', True),
            'preserve_activities': preserve.get('activities', True),
            'preserve_attachments': preserve.get('attachments', True),
        })
        others.write({'active': False})
        _logger.info('Merged leads %s into %s log=%s', ids, master.id, log.id)
        return log
