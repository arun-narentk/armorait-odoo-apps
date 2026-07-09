# -*- coding: utf-8 -*-

from odoo import models


class PurchaseOrder(models.Model):
    _inherit = ['purchase.order', 'rn.workflow.mixin']
