# -*- coding: utf-8 -*-

from odoo import _, api, fields, models


class ProfitGuardDashboard(models.Model):
    _name = 'profit.guard.dashboard'
    _description = 'Inventory & Margin Intelligence Dashboard'
    _rec_name = 'company_id'

    company_id = fields.Many2one('res.company', string='Company', required=True, default=lambda self: self.env.company, ondelete='cascade')
    currency_id = fields.Many2one(related='company_id.currency_id', string='Currency', readonly=True)
    total_dead_stock_value = fields.Float(string='Total Dead Stock Value', compute='_compute_kpis', store=False)
    total_slow_stock_value = fields.Float(string='Total Slow Stock Value', compute='_compute_kpis', store=False)
    total_capital_locked = fields.Float(string='Total Capital Locked', compute='_compute_kpis', store=False)
    margin_violations_count = fields.Integer(string='Margin Violations (This Month)', compute='_compute_kpis', store=False)

    @api.depends('company_id')
    def _compute_kpis(self):
        for rec in self:
            if not rec.company_id:
                rec.total_dead_stock_value = rec.total_slow_stock_value = rec.total_capital_locked = 0.0
                rec.margin_violations_count = 0
                continue
            products = self.env['product.product'].with_company(rec.company_id).search([
                ('type', '=', 'product'),
                ('dead_stock_status', 'in', ('dead', 'slow')),
            ])
            rec.total_dead_stock_value = sum(products.filtered(lambda p: p.dead_stock_status == 'dead').mapped('capital_locked'))
            rec.total_slow_stock_value = sum(products.filtered(lambda p: p.dead_stock_status == 'slow').mapped('capital_locked'))
            rec.total_capital_locked = sum(products.mapped('capital_locked'))
            from datetime import date
            start = date.today().replace(day=1)
            rec.margin_violations_count = self.env['margin.violation.log'].search_count([
                ('company_id', '=', rec.company_id.id),
                ('create_date', '>=', start),
            ])

    @api.model
    def _get_or_create_dashboard(self):
        company = self.env.company
        dash = self.search([('company_id', '=', company.id)], limit=1)
        if not dash:
            dash = self.create([{'company_id': company.id}])
        return dash

    @api.model
    def action_open_dashboard(self):
        dash = self._get_or_create_dashboard()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Inventory & Margin Intelligence'),
            'res_model': 'profit.guard.dashboard',
            'res_id': dash.id,
            'view_mode': 'form',
            'target': 'current',
        }
