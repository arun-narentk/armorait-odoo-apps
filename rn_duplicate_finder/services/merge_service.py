# -*- coding: utf-8 -*-
"""Record merge helpers."""

import logging

from odoo import _, models
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class RnDupMergeService(models.AbstractModel):
    _name = 'rn.dup.merge.service'
    _description = 'Duplicate Merge Service'

    def merge_records(self, model_name, master_id, duplicate_id, result=None):
        if master_id == duplicate_id:
            raise UserError(_('Select two different records to merge.'))
        if model_name not in self.env:
            raise UserError(_('Model %s is not available.') % model_name)
        Model = self.env[model_name]
        master = Model.browse(master_id).exists()
        duplicate = Model.browse(duplicate_id).exists()
        if not master or not duplicate:
            raise UserError(_('One or both records no longer exist.'))

        if model_name == 'res.partner':
            self._merge_partners(master, duplicate)
        else:
            self._archive_duplicate(master, duplicate)

        if result:
            result.write({'state': 'merged'})
        return master

    def _merge_partners(self, master, duplicate):
        wizard = self.env['base.partner.merge.automatic.wizard'].sudo()
        wizard._merge([master.id, duplicate.id], dst_partner=master, extra_checks=False)

    def _archive_duplicate(self, master, duplicate):
        vals = {}
        if 'active' in duplicate._fields:
            vals['active'] = False
        if vals:
            duplicate.write(vals)
        if hasattr(master, 'message_post'):
            master.message_post(
                body=_('Merged duplicate record %(dup)s into this record via Smart Duplicate Finder.',
                       dup=duplicate.display_name),
            )
