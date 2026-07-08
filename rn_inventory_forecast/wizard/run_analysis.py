# -*- coding: utf-8 -*-
"""Wizard to run ABC/XYZ/FSN analysis."""

from datetime import timedelta

from odoo import fields, models


class RnInvRunAnalysisWizard(models.TransientModel):
    """Select analysis type and period."""

    _name = 'rn.inv.run.analysis.wizard'
    _description = 'Run Inventory Analysis Wizard'

    analysis_type = fields.Selection(
        selection=[
            ('abc', 'ABC'),
            ('xyz', 'XYZ'),
            ('fsn', 'FSN'),
            ('all', 'All'),
        ],
        default='all',
        required=True,
    )
    date_from = fields.Date(
        required=True,
        default=lambda self: fields.Date.context_today(self) - timedelta(days=89),
    )
    date_to = fields.Date(required=True, default=fields.Date.context_today)
    warehouse_id = fields.Many2one('stock.warehouse')
    company_id = fields.Many2one(
        'res.company',
        required=True,
        default=lambda self: self.env.company,
    )

    def action_run(self):
        self.ensure_one()
        wh = self.warehouse_id.id if self.warehouse_id else None
        if self.analysis_type in ('abc', 'all'):
            self.env['rn.inv.abc.service'].run_analysis(
                self.date_from, self.date_to, company_id=self.company_id.id, warehouse_id=wh
            )
        if self.analysis_type in ('xyz', 'all'):
            self.env['rn.inv.xyz.service'].run_analysis(
                self.date_from, self.date_to, company_id=self.company_id.id, warehouse_id=wh
            )
        if self.analysis_type in ('fsn', 'all'):
            self.env['rn.inv.fsn.service'].run_analysis(
                self.date_from, self.date_to, company_id=self.company_id.id, warehouse_id=wh
            )
        return {
            'type': 'ir.actions.act_window',
            'name': 'Analysis Results',
            'res_model': 'rn.inv.analysis',
            'view_mode': 'list,form',
            'domain': [('company_id', '=', self.company_id.id)],
        }
