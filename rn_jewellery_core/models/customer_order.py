# -*- coding: utf-8 -*-

from odoo import api, fields, models


class RnJewelleryCustomerOrder(models.Model):
    _name = 'rn.jewellery.customer.order'
    _description = 'Custom Jewellery Order'
    _inherit = ['mail.thread']
    _order = 'order_date desc'

    name = fields.Char(readonly=True, copy=False, default='New')
    partner_id = fields.Many2one('res.partner', required=True, string='Customer', index=True)
    order_date = fields.Date(required=True, default=fields.Date.context_today)
    design_description = fields.Text()
    metal_type = fields.Selection(
        [('gold', 'Gold'), ('silver', 'Silver'), ('platinum', 'Platinum')],
        default='gold',
    )
    purity_id = fields.Many2one('rn.jewellery.metal.purity')
    estimated_weight = fields.Float(digits=(16, 3))
    advance_amount = fields.Float()
    total_amount = fields.Float()
    delivery_date = fields.Date()
    state = fields.Selection(
        [
            ('draft', 'Draft'),
            ('confirmed', 'Confirmed'),
            ('in_production', 'In Production'),
            ('ready', 'Ready'),
            ('delivered', 'Delivered'),
            ('cancelled', 'Cancelled'),
        ],
        default='draft',
        tracking=True,
    )
    job_card_ids = fields.One2many('rn.jewellery.job.card', 'customer_order_id')
    company_id = fields.Many2one(
        'res.company',
        required=True,
        default=lambda self: self.env.company,
        index=True,
    )

    @api.model_create_multi
    def create(self, vals_list):
        seq = self.env['ir.sequence']
        for vals in vals_list:
            if vals.get('name', 'New') == 'New':
                vals['name'] = seq.next_by_code('rn.jewellery.customer.order') or 'CO'
        return super().create(vals_list)
