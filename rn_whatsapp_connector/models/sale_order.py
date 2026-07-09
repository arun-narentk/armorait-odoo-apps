# -*- coding: utf-8 -*-
"""Sale order WhatsApp automation hooks."""

from odoo import models


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def action_confirm(self):
        res = super().action_confirm()
        self.env['rn.whatsapp.automation.service'].run_trigger('sale_order_confirmed', self)
        return res
