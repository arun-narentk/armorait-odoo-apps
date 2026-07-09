# -*- coding: utf-8 -*-
"""Settings bridge for MES configuration."""

from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    mes_auto_oee_snapshot = fields.Boolean(
        related='company_id.rn_mes_auto_oee_snapshot',
        readonly=False,
    )
    mes_require_quality_on_complete = fields.Boolean(
        related='company_id.rn_mes_require_quality_on_complete',
        readonly=False,
    )
    mes_ai_insights_enabled = fields.Boolean(
        related='company_id.rn_mes_ai_insights_enabled',
        readonly=False,
    )
    mes_iot_gateway_url = fields.Char(
        related='company_id.rn_mes_iot_gateway_url',
        readonly=False,
    )


class ResCompany(models.Model):
    _inherit = 'res.company'

    rn_mes_auto_oee_snapshot = fields.Boolean(default=True)
    rn_mes_require_quality_on_complete = fields.Boolean(default=False)
    rn_mes_ai_insights_enabled = fields.Boolean(default=True)
    rn_mes_iot_gateway_url = fields.Char()

    def _get_mes_settings(self):
        self.ensure_one()
        Settings = self.env['rn.mes.settings']
        rec = Settings.search([('company_id', '=', self.id)], limit=1)
        if not rec:
            rec = Settings.create({'company_id': self.id})
        return rec

    @api.model_create_multi
    def create(self, vals_list):
        companies = super().create(vals_list)
        Settings = self.env['rn.mes.settings']
        for company in companies:
            if not Settings.search_count([('company_id', '=', company.id)]):
                Settings.create({'company_id': company.id})
        return companies
