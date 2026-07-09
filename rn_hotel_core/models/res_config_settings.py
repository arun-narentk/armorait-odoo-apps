# -*- coding: utf-8 -*-

from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    hotel_ai_pricing = fields.Boolean(related='company_id.rn_hotel_ai_pricing', readonly=False)
    hotel_ai_concierge = fields.Boolean(related='company_id.rn_hotel_ai_concierge', readonly=False)


class ResCompany(models.Model):
    _inherit = 'res.company'

    rn_hotel_ai_pricing = fields.Boolean(default=True)
    rn_hotel_ai_concierge = fields.Boolean(default=True)

    def _get_hotel_settings(self):
        self.ensure_one()
        Settings = self.env['rn.hotel.settings']
        rec = Settings.search([('company_id', '=', self.id)], limit=1)
        if not rec:
            rec = Settings.create({'company_id': self.id})
        return rec

    @api.model_create_multi
    def create(self, vals_list):
        companies = super().create(vals_list)
        Settings = self.env['rn.hotel.settings']
        for company in companies:
            if not Settings.search_count([('company_id', '=', company.id)]):
                Settings.create({'company_id': company.id})
        return companies
