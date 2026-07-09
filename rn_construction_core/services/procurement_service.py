# -*- coding: utf-8 -*-

from odoo import models


class RnConstructionProcurementService(models.AbstractModel):
    _name = 'rn.construction.procurement.service'
    _description = 'Procurement Service'

    def submit_material_request(self, request_id):
        req = self.env['rn.construction.material.request'].browse(request_id)
        req.write({'state': 'submitted'})
        return True

    def approve_material_request(self, request_id):
        req = self.env['rn.construction.material.request'].browse(request_id)
        req.write({'state': 'approved'})
        return True

    def create_purchase_order(self, request_id, partner_id=None):
        req = self.env['rn.construction.material.request'].browse(request_id)
        req.ensure_one()
        partner = partner_id or self.env.ref('base.res_partner_1', raise_if_not_found=False)
        po = self.env['purchase.order'].create({
            'partner_id': partner.id if partner else False,
            'origin': req.name,
            'order_line': [(0, 0, {
                'product_id': req.product_id.id,
                'product_qty': req.quantity,
                'name': req.product_id.display_name,
                'price_unit': req.product_id.standard_price,
            })],
        })
        req.write({'state': 'ordered', 'purchase_order_id': po.id})
        return po.id
