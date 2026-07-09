# -*- coding: utf-8 -*-

from odoo import fields, models


class RnTempleDonationWizard(models.TransientModel):
    _name = 'rn.temple.donation.wizard'
    _description = 'Quick Donation'

    devotee_id = fields.Many2one('rn.temple.devotee')
    donor_name = fields.Char()
    amount = fields.Float(required=True)
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
        ],
        default='general',
    )
    tax_receipt = fields.Boolean()

    def action_record(self):
        self.ensure_one()
        donation_id = self.env['rn.temple.donation.service'].record_donation(
            self.amount,
            devotee_id=self.devotee_id.id if self.devotee_id else None,
            donor_name=self.donor_name or (self.devotee_id.name if self.devotee_id else None),
            payment_mode=self.payment_mode,
            purpose=self.purpose,
        )
        donation = self.env['rn.temple.donation'].browse(donation_id)
        if self.tax_receipt:
            donation.tax_receipt = True
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'rn.temple.donation',
            'res_id': donation_id,
            'view_mode': 'form',
            'target': 'current',
        }
