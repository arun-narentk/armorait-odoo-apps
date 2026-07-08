# -*- coding: utf-8 -*-

from odoo import api, models

from . import notification_engine


class AccountMove(models.Model):
    _inherit = 'account.move'

    # Index for credit risk aggregation (company, state, payment_state, move_type, commercial_partner_id)
    _credit_risk_aggregate_idx = models.Index(
        '(company_id, state, payment_state, move_type, commercial_partner_id)'
    )

    def write(self, vals):
        res = super(AccountMove, self).write(vals)
        if 'payment_state' in vals or 'state' in vals:
            partners = self.mapped('partner_id')
            commercial_ids = partners.mapped('commercial_partner_id').ids
            all_partners = self.env['res.partner'].search([('commercial_partner_id', 'in', commercial_ids)])
            if all_partners:
                all_partners._compute_credit_risk()
        return res

    @api.model
    def _cron_whatsapp_overdue_reminder(self):
        notification_engine.process_overdue_invoices_cron(self.env)

    @api.model
    def _cron_whatsapp_retry_failed(self):
        notification_engine.retry_failed_messages(self.env)

    def _whatsapp_overdue_message(self, delay_days):
        self.ensure_one()
        return notification_engine.build_overdue_invoice_message(self, delay_days)
