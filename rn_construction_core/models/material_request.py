# -*- coding: utf-8 -*-

from odoo import api, fields, models


class RnConstructionMaterialRequest(models.Model):
    _name = 'rn.construction.material.request'
    _description = 'Site Material Request'
    _inherit = ['mail.thread']
    _order = 'request_date desc'

    name = fields.Char(readonly=True, copy=False, default='New')
    site_id = fields.Many2one('rn.construction.site', required=True, index=True)
    requested_by = fields.Many2one('hr.employee', string='Requested By')
    request_date = fields.Datetime(default=fields.Datetime.now, required=True)
    product_id = fields.Many2one('product.product', required=True)
    quantity = fields.Float(required=True, default=1.0)
    uom = fields.Char()
    state = fields.Selection(
        [
            ('draft', 'Draft'),
            ('submitted', 'Submitted'),
            ('approved', 'Approved'),
            ('ordered', 'PO Created'),
            ('received', 'Received'),
            ('rejected', 'Rejected'),
        ],
        default='draft',
        tracking=True,
    )
    purchase_order_id = fields.Many2one('purchase.order', copy=False)
    note = fields.Text()
    company_id = fields.Many2one(related='site_id.company_id', store=True, index=True)

    @api.model_create_multi
    def create(self, vals_list):
        seq = self.env['ir.sequence']
        for vals in vals_list:
            if vals.get('name', 'New') == 'New':
                vals['name'] = seq.next_by_code('rn.construction.material.request') or 'MR'
        return super().create(vals_list)
