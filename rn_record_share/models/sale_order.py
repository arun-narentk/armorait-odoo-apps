# -*- coding: utf-8 -*-

from odoo import models


class SaleOrder(models.Model):
    _name = 'sale.order'
    _inherit = ['sale.order', 'rn.share.mixin']
