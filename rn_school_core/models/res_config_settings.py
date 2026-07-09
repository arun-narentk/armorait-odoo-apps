# -*- coding: utf-8 -*-

from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    school_ai_report_comments = fields.Boolean(related='company_id.rn_school_ai_report_comments', readonly=False)
    school_ai_risk_detection = fields.Boolean(related='company_id.rn_school_ai_risk_detection', readonly=False)
    school_parent_portal = fields.Boolean(related='company_id.rn_school_parent_portal', readonly=False)


class ResCompany(models.Model):
    _inherit = 'res.company'

    rn_school_ai_report_comments = fields.Boolean(default=True)
    rn_school_ai_risk_detection = fields.Boolean(default=True)
    rn_school_parent_portal = fields.Boolean(default=True)

    def _get_school_settings(self):
        self.ensure_one()
        Settings = self.env['rn.school.settings']
        rec = Settings.search([('company_id', '=', self.id)], limit=1)
        if not rec:
            rec = Settings.create({'company_id': self.id})
        return rec

    @api.model_create_multi
    def create(self, vals_list):
        companies = super().create(vals_list)
        Settings = self.env['rn.school.settings']
        for company in companies:
            if not Settings.search_count([('company_id', '=', company.id)]):
                Settings.create({'company_id': company.id})
        return companies
