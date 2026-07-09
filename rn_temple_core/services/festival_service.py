# -*- coding: utf-8 -*-

from odoo import fields, models


class RnTempleFestivalService(models.AbstractModel):
    _name = 'rn.temple.festival.service'
    _description = 'Festival Service'

    def activate_festival(self, festival_id):
        fest = self.env['rn.temple.festival'].browse(festival_id)
        fest.write({'state': 'active'})
        return True

    def festival_donation_summary(self, festival_id):
        fest = self.env['rn.temple.festival'].browse(festival_id)
        donations = fest.donation_ids.filtered(lambda d: d.state == 'confirmed')
        return {
            'festival': fest.name,
            'donation_count': len(donations),
            'donation_total': sum(donations.mapped('amount')),
            'budget': fest.budget,
        }
