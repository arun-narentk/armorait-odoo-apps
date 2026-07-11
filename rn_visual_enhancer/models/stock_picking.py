# -*- coding: utf-8 -*-

from odoo import models


class StockPicking(models.Model):
    _inherit = ["stock.picking", "rn.color.mixin"]
