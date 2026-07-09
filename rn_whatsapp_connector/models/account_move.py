# -*- coding: utf-8 -*-
"""Invoice WhatsApp automation hooks."""

from odoo import models


class AccountMove(models.Model):
    _inherit = 'account.move'

    def action_post(self):
        res = super().action_post()
        invoices = self.filtered(lambda m: m.is_invoice(include_receipts=True))
        if invoices:
            self.env['rn.whatsapp.automation.service'].run_trigger('invoice_posted', invoices)
        return res
