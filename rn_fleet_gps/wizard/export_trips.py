# -*- coding: utf-8 -*-
from odoo import fields, models


class RnFleetExportTripsWizard(models.TransientModel):
    _name = 'rn.fleet.export.trips.wizard'
    _description = 'Export Fleet Trips'

    company_id = fields.Many2one('res.company', required=True, default=lambda self: self.env.company)
    limit = fields.Integer(default=500)

    def action_export(self):
        self.ensure_one()
        return self.env['rn.fleet.export.service'].export_trips_csv(
            company_id=self.company_id.id,
            limit=self.limit,
        )
