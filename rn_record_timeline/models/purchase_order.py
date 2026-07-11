# -*- coding: utf-8 -*-

from odoo import _, models


class PurchaseOrder(models.Model):
    _inherit = ['purchase.order', 'rn.timeline.mixin']

    def _timeline_created_label(self):
        return _('RFQ Created')
