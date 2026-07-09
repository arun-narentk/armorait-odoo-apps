# -*- coding: utf-8 -*-

from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    construction_ai_cost = fields.Boolean(related='company_id.rn_construction_ai_cost', readonly=False)
    construction_ai_summary = fields.Boolean(related='company_id.rn_construction_ai_summary', readonly=False)


class ResCompany(models.Model):
    _inherit = 'res.company'

    rn_construction_ai_cost = fields.Boolean(default=True)
    rn_construction_ai_summary = fields.Boolean(default=True)

    def _get_construction_settings(self):
        self.ensure_one()
        Settings = self.env['rn.construction.settings']
        rec = Settings.search([('company_id', '=', self.id)], limit=1)
        if not rec:
            rec = Settings.create({'company_id': self.id})
        return rec

    @api.model_create_multi
    def create(self, vals_list):
        companies = super().create(vals_list)
        Settings = self.env['rn.construction.settings']
        for company in companies:
            if not Settings.search_count([('company_id', '=', company.id)]):
                Settings.create({'company_id': company.id})
        return companies
