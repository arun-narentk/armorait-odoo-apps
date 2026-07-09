# -*- coding: utf-8 -*-
"""Wizard to create and run a forecast."""

from datetime import timedelta

from odoo import fields, models


class RnInvGenerateForecastWizard(models.TransientModel):
    """Collect parameters then generate a forecast run."""

    _name = 'rn.inv.generate.forecast.wizard'
    _description = 'Generate Inventory Forecast Wizard'

    period_type = fields.Selection(
        selection=[
            ('daily', 'Daily'),
            ('weekly', 'Weekly'),
            ('monthly', 'Monthly'),
        ],
        default='weekly',
        required=True,
    )
    date_from = fields.Date(
        required=True,
        default=lambda self: fields.Date.context_today(self) - timedelta(days=89),
    )
    date_to = fields.Date(required=True, default=fields.Date.context_today)
    horizon_days = fields.Integer(default=30)
    warehouse_id = fields.Many2one('stock.warehouse')
    company_id = fields.Many2one(
        'res.company',
        required=True,
        default=lambda self: self.env.company,
    )

    def action_generate(self):
        self.ensure_one()
        run = self.env['rn.inv.forecast.run'].create({
            'name': 'Forecast %s' % self.date_to,
            'period_type': self.period_type,
            'date_from': self.date_from,
            'date_to': self.date_to,
            'horizon_days': self.horizon_days,
            'warehouse_id': self.warehouse_id.id if self.warehouse_id else False,
            'company_id': self.company_id.id,
        })
        run.action_generate()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Forecast Run',
            'res_model': 'rn.inv.forecast.run',
            'res_id': run.id,
            'view_mode': 'form',
            'target': 'current',
        }
