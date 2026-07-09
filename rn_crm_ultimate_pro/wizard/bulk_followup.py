# -*- coding: utf-8 -*-
"""Bulk follow-up scheduling wizard."""

from odoo import fields, models


class RnCrmBulkFollowupWizard(models.TransientModel):
    """Create reminders for a set of leads."""

    _name = 'rn.crm.bulk.followup.wizard'
    _description = 'Bulk Follow-up'

    lead_ids = fields.Many2many('crm.lead', string='Leads')
    schedule_at = fields.Datetime(required=True, default=fields.Datetime.now)
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
    body = fields.Text(default='Please follow up with this lead.')

    def action_schedule(self):
        self.ensure_one()
        Reminder = self.env['rn.crm.reminder']
        for lead in self.lead_ids:
            Reminder.create({
                'name': 'Follow-up: %s' % lead.display_name,
                'lead_id': lead.id,
                'user_id': lead.user_id.id,
                'schedule_at': self.schedule_at,
                'channel': self.channel,
                'body': self.body,
            })
        return {'type': 'ir.actions.act_window_close'}
