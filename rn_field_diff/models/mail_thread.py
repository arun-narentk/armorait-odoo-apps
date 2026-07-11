# -*- coding: utf-8 -*-

from odoo import models


class MailThread(models.AbstractModel):
    _inherit = 'mail.thread'

    def _track_prepare(self, fields_iter):
        """Allow tracked writes after record creation.

        Odoo discards tracking on create, leaving ``{record_id: None}`` in
        precommit data. Without resetting that entry, later writes skip field
        tracking for the same record in the same transaction.
        """
        key = f'mail.tracking.{self._name}'
        initial_values = self.env.cr.precommit.data.get(key)
        if initial_values:
            for record in self:
                if initial_values.get(record.id) is None:
                    initial_values[record.id] = {}
        return super()._track_prepare(fields_iter)
