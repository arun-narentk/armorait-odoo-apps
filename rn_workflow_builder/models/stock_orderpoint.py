# -*- coding: utf-8 -*-

from odoo import models


class StockWarehouseOrderpoint(models.Model):
    _inherit = ['stock.warehouse.orderpoint', 'rn.workflow.mixin']
