# -*- coding: utf-8 -*-

from odoo import models


class RnJewelleryRepairService(models.AbstractModel):
    _name = 'rn.jewellery.repair.service'
    _description = 'Repair Service'

    def mark_ready(self, repair_id):
        self.env['rn.jewellery.repair.order'].browse(repair_id).write({'state': 'ready'})
        return True

    def deliver(self, repair_id):
        self.env['rn.jewellery.repair.order'].browse(repair_id).write({'state': 'delivered'})
        return True
