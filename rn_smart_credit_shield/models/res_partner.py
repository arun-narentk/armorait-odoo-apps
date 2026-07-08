# -*- coding: utf-8 -*-

from odoo import api, fields, models

from . import credit_engine


class ResPartner(models.Model):
    _inherit = 'res.partner'

    credit_risk_score = fields.Float(
        string='Credit Risk Score',
        compute='_compute_credit_risk',
        store=True,
        digits=(5, 2),
        help='Weighted score 0–100. Derived from overdue ratio, avg delay, unpaid count, exposure.',
    )
    credit_risk_level = fields.Selection(
        [
            ('low', 'Low'),
            ('medium', 'Medium'),
            ('high', 'High'),
            ('critical', 'Critical'),
        ],
        string='Credit Risk Level',
        compute='_compute_credit_risk',
        store=True,
        index=True,
    )
    avg_payment_delay = fields.Float(
        string='Average Payment Delay (Days)',
        compute='_compute_credit_risk',
        store=True,
        digits=(16, 2),
        help='Average days overdue for unpaid invoices; or average delay for paid ones when available.',
    )

    @api.depends_context('company')
    @api.depends(
        'credit',
        'invoice_ids',
        'invoice_ids.state',
        'invoice_ids.payment_state',
        'invoice_ids.invoice_date_due',
        'invoice_ids.amount_residual',
    )
    def _compute_credit_risk(self):
        if not self:
            return

        results = credit_engine.CreditRiskEngine.compute_risk_for_partners(self.env, self)
        if not results:
            for partner in self:
                partner.credit_risk_score = 0.0
                partner.credit_risk_level = 'low'
                partner.avg_payment_delay = 0.0
            return

        for partner in self:
            commercial_id = partner.commercial_partner_id.id
            data = results.get(commercial_id)
            if not data:
                partner.credit_risk_score = 0.0
                partner.credit_risk_level = 'low'
                partner.avg_payment_delay = 0.0
                continue
            partner.credit_risk_score = data['score']
            partner.credit_risk_level = data['level']
            partner.avg_payment_delay = data['avg_delay']
