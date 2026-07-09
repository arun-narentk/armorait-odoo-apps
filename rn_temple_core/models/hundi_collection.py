# -*- coding: utf-8 -*-

from odoo import api, fields, models


class RnTempleHundiCollection(models.Model):
    _name = 'rn.temple.hundi.collection'
    _description = 'Hundi Collection'
    _inherit = ['mail.thread']
    _order = 'collection_date desc'

    name = fields.Char(readonly=True, copy=False, default='New')
    collection_date = fields.Date(required=True, default=fields.Date.context_today, index=True)
    counting_team = fields.Char()
    amount_counted = fields.Float(required=True)
    amount_verified = fields.Float()
    deposited_amount = fields.Float()
    deposit_date = fields.Date()
    bank_reference = fields.Char()
    state = fields.Selection(
        [
            ('draft', 'Draft'),
            ('counted', 'Counted'),
            ('verified', 'Verified'),
            ('deposited', 'Deposited'),
        ],
        default='draft',
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
                vals['name'] = seq.next_by_code('rn.temple.hundi.collection') or 'HUN'
        return super().create(vals_list)
