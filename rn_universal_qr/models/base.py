# -*- coding: utf-8 -*-
from odoo import models


class Base(models.AbstractModel):
    _name = 'base'
    _inherit = ['base', 'rn.qr.mixin']

# -*- coding: utf-8 -*-
from odoo import models


class Base(models.AbstractModel):
    _name = 'base'
    _inherit = ['base', 'rn.qr.mixin']
# -*- coding: utf-8 -*-
"""Attach Universal QR mixin to every Odoo model."""

from odoo import api, models


class Base(models.AbstractModel):
    _inherit = ['base', 'rn.qr.mixin']

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        if self.env.context.get('rn_qr_skip_auto'):
            return records
        configs = self.env['rn.qr.model.config'].sudo().search([
            ('model_name', '=', self._name),
            ('auto_generate', '=', True),
            ('active', '=', True),
        ], limit=1)
        if configs:
            service = self.env['rn.qr.service']
            values = configs.get_values_for_record()
            for record in records:
                service.get_or_create_qr(self._name, record.id, values)
        return records
