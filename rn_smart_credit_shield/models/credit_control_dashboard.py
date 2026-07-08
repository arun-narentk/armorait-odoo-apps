# -*- coding: utf-8 -*-

from odoo import _, api, fields, models
from odoo.tools import format_amount
from datetime import timedelta


class CreditControlDashboard(models.Model):
    _name = 'credit.control.dashboard'
    _description = 'Credit Control Dashboard'
    _rec_name = 'company_id'

    company_id = fields.Many2one('res.company', string='Company', required=True, default=lambda self: self.env.company, ondelete='cascade')
    currency_id = fields.Many2one(related='company_id.currency_id', string='Currency', readonly=True)
    total_exposure = fields.Float(string='Total Exposure', compute='_compute_kpis', store=False)
    total_receivable = fields.Float(string='Total Receivable', compute='_compute_kpis', store=False)
    high_risk_count = fields.Integer(string='High-Risk Count', compute='_compute_kpis', store=False)
    critical_count = fields.Integer(string='Critical Count', compute='_compute_kpis', store=False)
    avg_delay = fields.Float(string='Avg Payment Delay (Days)', compute='_compute_kpis', store=False)
    overdue_invoices_count = fields.Integer(string='Overdue Invoices', compute='_compute_kpis', store=False)
    overdue_90_count = fields.Integer(string='Overdue > 90 Days', compute='_compute_kpis', store=False, help='Invoices overdue more than 90 days.')
    blocked_so_count = fields.Integer(string='Blocked Sales Orders', compute='_compute_kpis', store=False)
    violations_this_month = fields.Integer(string='Credit Violations This Month', compute='_compute_kpis', store=False)
    # Risk distribution for heatmap
    count_low = fields.Integer(compute='_compute_kpis', store=False)
    count_medium = fields.Integer(compute='_compute_kpis', store=False)
    count_high = fields.Integer(compute='_compute_kpis', store=False)
    count_critical = fields.Integer(compute='_compute_kpis', store=False)
    # Top 10 risky (HTML for inline display)
    top_10_risky_html = fields.Html(string='Top 10 Risky Partners', compute='_compute_top_10_risky', sanitize=False)

    @api.depends('company_id')
    def _compute_kpis(self):
        for rec in self:
            if not rec.company_id:
                rec.total_exposure = rec.total_receivable = 0.0
                rec.high_risk_count = rec.critical_count = rec.overdue_invoices_count = 0
                rec.overdue_90_count = rec.blocked_so_count = rec.violations_this_month = 0
                rec.avg_delay = 0.0
                rec.count_low = rec.count_medium = rec.count_high = rec.count_critical = 0
                continue
            Partner = self.env['res.partner'].with_company(rec.company_id)
            domain_customers = ['|', ('customer_rank', '>', 0), ('supplier_rank', '>', 0)]
            high_critical = Partner.search([
                ('credit_risk_level', 'in', ('high', 'critical')),
                *domain_customers,
            ])
            rec.high_risk_count = len(high_critical)
            rec.critical_count = len(high_critical.filtered(lambda p: p.credit_risk_level == 'critical'))
            rec.total_exposure = sum(high_critical.mapped('credit'))
            rec.avg_delay = sum(high_critical.mapped('avg_payment_delay')) / len(high_critical) if high_critical else 0.0
            # All with risk level (customers)
            with_level = Partner.search([('credit_risk_level', '!=', False), *domain_customers])
            rec.total_receivable = sum(with_level.mapped('credit'))
            rec.count_low = len(with_level.filtered(lambda p: p.credit_risk_level == 'low'))
            rec.count_medium = len(with_level.filtered(lambda p: p.credit_risk_level == 'medium'))
            rec.count_high = len(with_level.filtered(lambda p: p.credit_risk_level == 'high'))
            rec.count_critical = len(with_level.filtered(lambda p: p.credit_risk_level == 'critical'))
            rec.overdue_invoices_count = self.env['account.move'].search_count([
                ('company_id', '=', rec.company_id.id),
                ('move_type', 'in', ('out_invoice', 'out_refund', 'out_receipt')),
                ('state', '=', 'posted'),
                ('payment_state', 'not in', ('paid', 'reversed')),
                ('invoice_date_due', '<', fields.Date.context_today(self)),
            ])
            today = fields.Date.context_today(self)
            limit_90 = today - timedelta(days=90)
            rec.overdue_90_count = self.env['account.move'].search_count([
                ('company_id', '=', rec.company_id.id),
                ('move_type', 'in', ('out_invoice', 'out_refund', 'out_receipt')),
                ('state', '=', 'posted'),
                ('payment_state', 'not in', ('paid', 'reversed')),
                ('invoice_date_due', '<', limit_90),
            ])
            rec.blocked_so_count = self.env['sale.order'].search_count([
                ('company_id', '=', rec.company_id.id),
                ('credit_blocked', '=', True),
                ('state', 'not in', ('sale', 'done', 'cancel')),
            ])
            start_month = today.replace(day=1)
            rec.violations_this_month = self.env['credit.violation.log'].search_count([
                ('company_id', '=', rec.company_id.id),
                ('create_date', '>=', start_month),
            ])

    @api.depends('company_id')
    def _compute_top_10_risky(self):
        for rec in self:
            if not rec.company_id:
                rec.top_10_risky_html = '<p class="text-muted">No data</p>'
                continue
            partners = self.env['res.partner'].with_company(rec.company_id).search([
                ('credit_risk_level', 'in', ('high', 'critical')),
                '|', ('customer_rank', '>', 0), ('supplier_rank', '>', 0),
            ], order='credit_risk_score desc', limit=10)
            if not partners:
                rec.top_10_risky_html = '<p class="text-muted">No high-risk or critical partners</p>'
                continue
            rows = []
            for p in partners:
                level_class = 'danger' if p.credit_risk_level == 'critical' else 'warning'
                url = '/web#model=res.partner&amp;id=%s&amp;view_type=form' % p.id
                amount = format_amount(p.credit or 0, rec.currency_id) if rec.currency_id else '%.2f' % (p.credit or 0)
                rows.append(
                    '<tr><td><a href="%s">%s</a></td><td class="text-nowrap"><span class="badge badge-%s">%s</span></td>'
                    '<td>%.1f</td><td>%s</td></tr>' % (
                        url, p.name or 'Partner', level_class, p.credit_risk_level.upper(), p.credit_risk_score or 0, amount
                    )
                )
            rec.top_10_risky_html = (
                '<div class="table-responsive"><table class="table table-sm table-hover table-borderless">'
                '<thead><tr><th>Partner</th><th>Level</th><th>Score</th><th>Exposure</th></tr></thead><tbody>%s</tbody></table></div>'
            ) % ''.join(rows)

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
            'name': _('Credit Control Dashboard'),
            'res_model': 'credit.control.dashboard',
            'res_id': dash.id,
            'view_mode': 'form',
            'target': 'current',
        }

    def action_top_10_risky(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Top 10 Risky Partners'),
            'res_model': 'res.partner',
            'view_mode': 'list,form',
            'domain': [
                ('credit_risk_level', 'in', ('high', 'critical')),
                '|', ('customer_rank', '>', 0), ('supplier_rank', '>', 0),
            ],
            'context': {'search_default_customer': 1},
        }

    def action_overdue_invoices(self):
        return self.env.ref('rn_smart_credit_shield.action_account_move_overdue').read()[0]

    def action_whatsapp_log(self):
        return self.env.ref('rn_smart_credit_shield.action_whatsapp_message_log').read()[0]

    def action_credit_violations(self):
        return self.env.ref('rn_smart_credit_shield.action_credit_violation_log').read()[0]

    def action_blocked_so(self):
        return self.env.ref('rn_smart_credit_shield.action_sale_order_blocked').read()[0]
