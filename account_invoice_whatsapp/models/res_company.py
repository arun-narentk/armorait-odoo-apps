# -*- coding: utf-8 -*-

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class ResCompany(models.Model):
    _inherit = 'res.company'

    # Unpaid invoice follow-up
    whatsapp_invoice_followup = fields.Boolean(
        string='WhatsApp Unpaid Invoice Follow-up',
        default=False,
        help='Create WhatsApp reminders for overdue unpaid customer invoices.',
    )
    whatsapp_invoice_followup_days = fields.Integer(
        string='Days After Due for First Reminder',
        default=1,
        help='Create reminder this many days after invoice due date.',
    )
    # Payment reminder (same as invoice follow-up or separate logic)
    whatsapp_payment_reminder = fields.Boolean(
        string='WhatsApp Payment Reminder',
        default=False,
        help='Create WhatsApp payment reminders for partially paid or unpaid invoices.',
    )
    # Sales follow-up sequence
    whatsapp_sales_followup = fields.Boolean(
        string='WhatsApp Sales Follow-up',
        default=False,
        help='Create WhatsApp follow-up reminders for quotations sent but not confirmed.',
    )
    whatsapp_sales_followup_days = fields.Integer(
        string='Days After Quotation Sent',
        default=3,
        help='Create sales follow-up reminder this many days after quotation is sent.',
    )
    # Delivery status alert
    whatsapp_delivery_alert = fields.Boolean(
        string='WhatsApp Delivery Status Alert',
        default=False,
        help='Create WhatsApp reminder when a delivery order is validated (done).',
    )
