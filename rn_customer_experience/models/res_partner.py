# -*- coding: utf-8 -*-

from odoo import fields, models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    experience_ticket_count = fields.Integer(compute='_compute_experience_counts')
    experience_warranty_count = fields.Integer(compute='_compute_experience_counts')
    experience_amc_count = fields.Integer(compute='_compute_experience_counts')

    def _compute_experience_counts(self):
        Ticket = self.env['rn.customer.experience.ticket']
        Warranty = self.env['rn.customer.experience.warranty']
        Amc = self.env['rn.customer.experience.amc']
        for partner in self:
            partner.experience_ticket_count = Ticket.search_count([('partner_id', '=', partner.id)])
            partner.experience_warranty_count = Warranty.search_count([('partner_id', '=', partner.id)])
            partner.experience_amc_count = Amc.search_count([('partner_id', '=', partner.id)])
