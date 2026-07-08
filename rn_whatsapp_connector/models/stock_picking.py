# -*- coding: utf-8 -*-
"""Delivery WhatsApp automation hooks."""

from odoo import models


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    def button_validate(self):
        res = super().button_validate()
        done = self.filtered(lambda p: p.state == 'done')
        if done:
            self.env['rn.whatsapp.automation.service'].run_trigger('delivery_completed', done)
        return res
