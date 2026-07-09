# -*- coding: utf-8 -*-

from odoo import fields, models


class RnConstructionMaterialRequestWizard(models.TransientModel):
    _name = 'rn.construction.material.request.wizard'
    _description = 'Quick Material Request'

    site_id = fields.Many2one('rn.construction.site', required=True)
    product_id = fields.Many2one('product.product', required=True)
    quantity = fields.Float(required=True, default=1.0)
    note = fields.Text()

    def action_submit(self):
        self.ensure_one()
        req = self.env['rn.construction.material.request'].create({
            'site_id': self.site_id.id,
            'product_id': self.product_id.id,
            'quantity': self.quantity,
            'note': self.note,
            'state': 'submitted',
        })
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'rn.construction.material.request',
            'res_id': req.id,
            'view_mode': 'form',
            'target': 'current',
        }
