# -*- coding: utf-8 -*-
"""Export menu catalog wizard."""

from odoo import fields, models


class RnRestaurantExportMenuWizard(models.TransientModel):
    _name = 'rn.restaurant.export.menu.wizard'
    _description = 'Export Restaurant Menu'

    restaurant_id = fields.Many2one('rn.restaurant', required=True)

    def action_export(self):
        self.ensure_one()
        return self.env['rn.restaurant.export.service'].export_menu_csv(self.restaurant_id)
