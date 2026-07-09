# -*- coding: utf-8 -*-
"""Forecast run container."""

from odoo import api, fields, models


class RnInvForecastRun(models.Model):
    """One forecast generation batch for a company/warehouse."""

    _name = 'rn.inv.forecast.run'
    _description = 'Inventory Forecast Run'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'date_to desc, id desc'

    name = fields.Char(required=True, tracking=True)
    state = fields.Selection(
        selection=[
            ('draft', 'Draft'),
            ('running', 'Running'),
            ('done', 'Done'),
            ('cancel', 'Cancelled'),
        ],
        default='draft',
        tracking=True,
    )
    period_type = fields.Selection(
        selection=[
            ('daily', 'Daily'),
            ('weekly', 'Weekly'),
            ('monthly', 'Monthly'),
        ],
        default='weekly',
        required=True,
    )
    date_from = fields.Date(required=True)
    date_to = fields.Date(required=True)
    horizon_days = fields.Integer(default=30, help='Future days to forecast.')
    warehouse_id = fields.Many2one('stock.warehouse', string='Warehouse')
    company_id = fields.Many2one(
        'res.company',
        required=True,
        default=lambda self: self.env.company,
        index=True,
    )
    line_ids = fields.One2many('rn.inv.forecast.line', 'run_id', string='Forecast Lines')
    line_count = fields.Integer(compute='_compute_line_count')
    accuracy_pct = fields.Float(string='Forecast Accuracy %', digits=(16, 2))
    note = fields.Text()

    @api.depends('line_ids')
    def _compute_line_count(self):
        for run in self:
            run.line_count = len(run.line_ids)

    def action_generate(self):
        """Generate forecast lines via service layer."""
        self.ensure_one()
        self.state = 'running'
        self.env['rn.inv.forecast.service'].generate_run(self)
        self.state = 'done'
        return True

    def action_cancel(self):
        self.write({'state': 'cancel'})
        return True

    def action_open_lines(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Forecast Lines',
            'res_model': 'rn.inv.forecast.line',
            'view_mode': 'list,form',
            'domain': [('run_id', '=', self.id)],
        }
