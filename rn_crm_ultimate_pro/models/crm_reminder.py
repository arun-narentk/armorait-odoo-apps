# -*- coding: utf-8 -*-
"""Reminder queue for salespeople and managers."""

from odoo import fields, models


class RnCrmReminder(models.Model):
    """Queued reminder to be delivered via mail, chatter, or hooks."""

    _name = 'rn.crm.reminder'
    _description = 'CRM Reminder'
    _order = 'schedule_at, id'

    name = fields.Char(required=True)
    lead_id = fields.Many2one('crm.lead', ondelete='cascade', index=True)
    user_id = fields.Many2one('res.users', string='Salesperson')
    schedule_at = fields.Datetime(required=True)
    channel = fields.Selection(
        selection=[
            ('activity', 'Activity'),
            ('email', 'Email'),
            ('browser', 'Browser Notification'),
            ('whatsapp', 'WhatsApp Hook'),
        ],
        default='activity',
        required=True,
    )
    state = fields.Selection(
        selection=[('pending', 'Pending'), ('sent', 'Sent'), ('cancelled', 'Cancelled')],
        default='pending',
        index=True,
    )
    body = fields.Text()
    company_id = fields.Many2one('res.company', default=lambda self: self.env.company)
