# -*- coding: utf-8 -*-

from odoo import _, models


class SaleOrder(models.Model):
    _inherit = ['sale.order', 'rn.timeline.mixin']

    def _timeline_created_label(self):
        return _('Quotation Created')
