# -*- coding: utf-8 -*-

from odoo import models


class RnJewelleryOrderService(models.AbstractModel):
    _name = 'rn.jewellery.order.service'
    _description = 'Customer Order Service'

    def confirm_order(self, order_id):
        order = self.env['rn.jewellery.customer.order'].browse(order_id)
        order.write({'state': 'confirmed'})
        return True

    def start_production(self, order_id):
        order = self.env['rn.jewellery.customer.order'].browse(order_id)
        order.write({'state': 'in_production'})
        if not order.job_card_ids:
            self.env['rn.jewellery.job.card'].create({
                'design_code': order.name,
                'description': order.design_description,
                'customer_order_id': order.id,
                'metal_type': order.metal_type,
                'purity_id': order.purity_id.id,
                'state': 'in_progress',
            })
        return True

    def mark_delivered(self, order_id):
        order = self.env['rn.jewellery.customer.order'].browse(order_id)
        order.write({'state': 'delivered'})
        return True
