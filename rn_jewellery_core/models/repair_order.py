# -*- coding: utf-8 -*-

from odoo import api, fields, models


class RnJewelleryRepairOrder(models.Model):
    _name = 'rn.jewellery.repair.order'
    _description = 'Jewellery Repair Order'
    _inherit = ['mail.thread']
    _order = 'receive_date desc'

    name = fields.Char(readonly=True, copy=False, default='New')
    partner_id = fields.Many2one('res.partner', required=True, string='Customer', index=True)
    item_description = fields.Char(required=True)
    repair_type = fields.Selection(
        [
            ('polishing', 'Polishing'),
            ('stone_replace', 'Stone Replacement'),
            ('resizing', 'Resizing'),
            ('general', 'General Repair'),
        ],
        default='general',
        required=True,
    )
    receive_date = fields.Date(required=True, default=fields.Date.context_today)
    promised_date = fields.Date()
    charge_amount = fields.Float()
    warranty = fields.Boolean()
    state = fields.Selection(
        [
            ('received', 'Received'),
            ('in_progress', 'In Progress'),
            ('ready', 'Ready for Pickup'),
            ('delivered', 'Delivered'),
            ('cancelled', 'Cancelled'),
        ],
        default='received',
        tracking=True,
    )
    note = fields.Text()
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
                vals['name'] = seq.next_by_code('rn.jewellery.repair.order') or 'REP'
        return super().create(vals_list)
