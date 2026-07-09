# -*- coding: utf-8 -*-

from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    dental_ai_notes = fields.Boolean(related='company_id.rn_dental_ai_notes', readonly=False)
    dental_ai_recall = fields.Boolean(related='company_id.rn_dental_ai_recall', readonly=False)


class ResCompany(models.Model):
    _inherit = 'res.company'

    rn_dental_ai_notes = fields.Boolean(default=True)
    rn_dental_ai_recall = fields.Boolean(default=True)

    def _get_dental_settings(self):
        self.ensure_one()
        Settings = self.env['rn.dental.settings']
        rec = Settings.search([('company_id', '=', self.id)], limit=1)
        if not rec:
            rec = Settings.create({'company_id': self.id})
        return rec

    @api.model_create_multi
    def create(self, vals_list):
        companies = super().create(vals_list)
        Settings = self.env['rn.dental.settings']
        for company in companies:
            if not Settings.search_count([('company_id', '=', company.id)]):
                Settings.create({'company_id': company.id})
        return companies
