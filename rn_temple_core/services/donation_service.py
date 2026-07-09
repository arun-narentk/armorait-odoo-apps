# -*- coding: utf-8 -*-

from odoo import fields, models


class RnTempleDonationService(models.AbstractModel):
    _name = 'rn.temple.donation.service'
    _description = 'Donation Service'

    def record_donation(self, amount, devotee_id=None, donor_name=None, payment_mode='cash', purpose='general'):
        devotee = self.env['rn.temple.devotee'].browse(devotee_id) if devotee_id else False
        donation = self.env['rn.temple.donation'].create({
            'devotee_id': devotee.id if devotee else False,
            'donor_name': donor_name or (devotee.name if devotee else 'Anonymous'),
            'amount': amount,
            'payment_mode': payment_mode,
            'purpose': purpose,
            'state': 'confirmed',
        })
        donation.action_confirm()
        return donation.id

    def search_donations(self, donor_name=None, festival_id=None, date_from=None, date_to=None):
        domain = [('state', '=', 'confirmed')]
        if donor_name:
            domain += ['|', ('donor_name', 'ilike', donor_name), ('devotee_id.name', 'ilike', donor_name)]
        if festival_id:
            domain.append(('festival_id', '=', festival_id))
        if date_from:
            domain.append(('donation_date', '>=', date_from))
        if date_to:
            domain.append(('donation_date', '<=', date_to))
        return self.env['rn.temple.donation'].search(domain)
