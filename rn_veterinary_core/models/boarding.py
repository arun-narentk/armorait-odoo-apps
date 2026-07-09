# -*- coding: utf-8 -*-

from odoo import api, fields, models


class RnVetBoarding(models.Model):
    _name = 'rn.vet.boarding'
    _description = 'Pet Boarding'
    _inherit = ['mail.thread']
    _order = 'check_in desc'

    name = fields.Char(readonly=True, copy=False, default='New')
    pet_id = fields.Many2one('rn.vet.pet', required=True, index=True)
    kennel_id = fields.Many2one('rn.vet.kennel', required=True, index=True)
    check_in = fields.Datetime(required=True)
    check_out = fields.Datetime()
    feeding_schedule = fields.Text()
    daily_rate = fields.Float()
    state = fields.Selection(
        [('reserved', 'Reserved'), ('checked_in', 'Checked In'), ('checked_out', 'Checked Out'), ('cancelled', 'Cancelled')],
        default='reserved',
        tracking=True,
    )
    note = fields.Text()
    company_id = fields.Many2one(related='pet_id.company_id', store=True, index=True)

    @api.model_create_multi
    def create(self, vals_list):
        seq = self.env['ir.sequence']
        for vals in vals_list:
            if vals.get('name', 'New') == 'New':
                vals['name'] = seq.next_by_code('rn.vet.boarding') or 'BRD'
        return super().create(vals_list)

    def action_check_in(self):
        self.write({'state': 'checked_in'})

    def action_check_out(self):
        self.write({'state': 'checked_out', 'check_out': fields.Datetime.now()})
