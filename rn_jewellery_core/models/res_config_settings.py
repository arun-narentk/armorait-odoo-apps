# -*- coding: utf-8 -*-

from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    jewellery_ai_pricing = fields.Boolean(related='company_id.rn_jewellery_ai_pricing', readonly=False)
    jewellery_ai_fraud = fields.Boolean(related='company_id.rn_jewellery_ai_fraud', readonly=False)


class ResCompany(models.Model):
    _inherit = 'res.company'

    rn_jewellery_ai_pricing = fields.Boolean(default=True)
    rn_jewellery_ai_fraud = fields.Boolean(default=True)

    def _get_jewellery_settings(self):
        self.ensure_one()
        Settings = self.env['rn.jewellery.settings']
        rec = Settings.search([('company_id', '=', self.id)], limit=1)
        if not rec:
            rec = Settings.create({'company_id': self.id})
        return rec

    @api.model_create_multi
    def create(self, vals_list):
        companies = super().create(vals_list)
        Settings = self.env['rn.jewellery.settings']
        for company in companies:
            if not Settings.search_count([('company_id', '=', company.id)]):
                Settings.create({'company_id': company.id})
        return companies
