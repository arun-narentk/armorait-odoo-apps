# -*- coding: utf-8 -*-
"""Mixin adding record share actions to business documents."""

from odoo import models


class RnShareMixin(models.AbstractModel):
    _name = 'rn.share.mixin'
    _description = 'Record Share Mixin'

    def action_copy_record_link(self):
        self.ensure_one()
        return self.env['rn.record.share.service'].copy_link_action(self)

    def action_open_record_share(self):
        self.ensure_one()
        return self.env['rn.record.share.wizard'].open_for_record(self._name, self.id)

    def action_open_record_qr(self):
        self.ensure_one()
        return self.env['rn.record.share.service'].open_qr_action(self)
