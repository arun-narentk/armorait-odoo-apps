# -*- coding: utf-8 -*-

from odoo import api, models


class MailTrackingValue(models.Model):
    _inherit = 'mail.tracking.value'

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        if not self.env.context.get('rn_skip_field_diff_sync'):
            service = self.env['rn.field.diff.service']
            for tracking in records:
                try:
                    service.sync_from_tracking(tracking)
                except Exception:
                    continue
        return records
