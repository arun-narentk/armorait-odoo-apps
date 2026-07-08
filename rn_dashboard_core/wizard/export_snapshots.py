# -*- coding: utf-8 -*-
"""Export KPI snapshots wizard."""

from odoo import fields, models


class RnDashboardExportWizard(models.TransientModel):
    _name = 'rn.dashboard.export.wizard'
    _description = 'Export Dashboard Snapshots'

    company_id = fields.Many2one(
        'res.company',
        required=True,
        default=lambda self: self.env.company,
    )
    limit = fields.Integer(default=500)

    def action_export(self):
        self.ensure_one()
        return self.env['rn.dashboard.export.service'].export_snapshots_csv(
            company_id=self.company_id.id,
            limit=self.limit,
        )
