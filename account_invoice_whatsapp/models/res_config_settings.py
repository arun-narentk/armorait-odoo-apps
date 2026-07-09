# -*- coding: utf-8 -*-

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    whatsapp_invoice_followup = fields.Boolean(
        related='company_id.whatsapp_invoice_followup',
        readonly=False,
    )
    whatsapp_invoice_followup_days = fields.Integer(
        related='company_id.whatsapp_invoice_followup_days',
        readonly=False,
    )
    whatsapp_payment_reminder = fields.Boolean(
        related='company_id.whatsapp_payment_reminder',
        readonly=False,
    )
    whatsapp_sales_followup = fields.Boolean(
        related='company_id.whatsapp_sales_followup',
        readonly=False,
    )
    whatsapp_sales_followup_days = fields.Integer(
        related='company_id.whatsapp_sales_followup_days',
        readonly=False,
    )
    whatsapp_delivery_alert = fields.Boolean(
        related='company_id.whatsapp_delivery_alert',
        readonly=False,
    )
