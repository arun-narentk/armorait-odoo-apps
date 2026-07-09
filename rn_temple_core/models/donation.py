# -*- coding: utf-8 -*-

from odoo import api, fields, models


class RnTempleDonation(models.Model):
    _name = 'rn.temple.donation'
    _description = 'Temple Donation'
    _inherit = ['mail.thread']
    _order = 'donation_date desc'

    name = fields.Char(readonly=True, copy=False, default='New')
    devotee_id = fields.Many2one('rn.temple.devotee', index=True)
    donor_name = fields.Char(string='Donor Name')
    amount = fields.Float(required=True)
    donation_date = fields.Datetime(default=fields.Datetime.now, required=True, index=True)
    payment_mode = fields.Selection(
        [
            ('cash', 'Cash'),
            ('upi', 'UPI'),
            ('card', 'Card'),
            ('bank', 'Bank Transfer'),
            ('cheque', 'Cheque'),
            ('online', 'Online'),
        ],
        default='cash',
        required=True,
    )
    purpose = fields.Selection(
        [
            ('general', 'General Fund'),
            ('annadhanam', 'Annadhanam'),
            ('festival', 'Festival'),
            ('seva', 'Seva'),
            ('hundi', 'Hundi'),
            ('construction', 'Construction'),
        ],
        default='general',
    )
    festival_id = fields.Many2one('rn.temple.festival')
    tax_receipt = fields.Boolean(string='Tax Receipt Required')
    receipt_number = fields.Char(readonly=True, copy=False)
    state = fields.Selection(
        [('draft', 'Draft'), ('confirmed', 'Confirmed'), ('cancelled', 'Cancelled')],
        default='draft',
        tracking=True,
    )
    invoice_id = fields.Many2one('account.move', copy=False)
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
                vals['name'] = seq.next_by_code('rn.temple.donation') or 'DON'
        return super().create(vals_list)

    def action_confirm(self):
        for rec in self:
            rec.state = 'confirmed'
            if not rec.receipt_number:
                rec.receipt_number = self.env['ir.sequence'].next_by_code('rn.temple.receipt') or rec.name
