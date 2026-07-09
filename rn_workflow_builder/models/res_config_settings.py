# -*- coding: utf-8 -*-

from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    wf_ai_builder_enabled = fields.Boolean(
        related='company_id.rn_wf_ai_builder_enabled',
        readonly=False,
    )
    wf_allow_external_webhooks = fields.Boolean(
        related='company_id.rn_wf_allow_external_webhooks',
        readonly=False,
    )
    wf_retry_failed_runs = fields.Boolean(
        related='company_id.rn_wf_retry_failed_runs',
        readonly=False,
    )


class ResCompany(models.Model):
    _inherit = 'res.company'

    rn_wf_ai_builder_enabled = fields.Boolean(default=True)
    rn_wf_allow_external_webhooks = fields.Boolean(default=True)
    rn_wf_retry_failed_runs = fields.Boolean(default=True)

    def _get_workflow_settings(self):
        self.ensure_one()
        Settings = self.env['rn.workflow.settings']
        rec = Settings.search([('company_id', '=', self.id)], limit=1)
        if not rec:
            rec = Settings.create({'company_id': self.id})
        return rec

    @api.model_create_multi
    def create(self, vals_list):
        companies = super().create(vals_list)
        Settings = self.env['rn.workflow.settings']
        for company in companies:
            if not Settings.search_count([('company_id', '=', company.id)]):
                Settings.create({'company_id': company.id})
        return companies
