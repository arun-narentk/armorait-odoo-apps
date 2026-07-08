# -*- coding: utf-8 -*-
"""Generic WhatsApp automation rules."""

from odoo import fields, models


class RnWhatsappAutomationRule(models.Model):
    """Trigger -> template mapping without hardcoding business events."""

    _name = 'rn.whatsapp.automation.rule'
    _description = 'WhatsApp Automation Rule'
    _inherit = ['mail.thread']
    _order = 'sequence, id'

    name = fields.Char(required=True, tracking=True)
    sequence = fields.Integer(default=10)
    active = fields.Boolean(default=True)
    trigger = fields.Selection(
        selection=[
            ('record_created', 'Record Created'),
            ('record_updated', 'Record Updated'),
            ('state_changed', 'State Changed'),
            ('sale_order_confirmed', 'Sale Order Confirmed'),
            ('invoice_posted', 'Invoice Posted'),
            ('payment_registered', 'Payment Registered'),
            ('delivery_completed', 'Delivery Completed'),
            ('lead_created', 'Lead Created'),
            ('opportunity_won', 'Opportunity Won'),
            ('appointment_confirmed', 'Appointment Confirmed'),
            ('purchase_approved', 'Purchase Order Approved'),
            ('mo_finished', 'Manufacturing Order Finished'),
            ('subscription_renewed', 'Subscription Renewed'),
            ('custom', 'Custom / Registered'),
        ],
        required=True,
        default='sale_order_confirmed',
        index=True,
        tracking=True,
    )
    model_id = fields.Many2one('ir.model', string='Model', ondelete='cascade', index=True)
    model_name = fields.Char(related='model_id.model', store=True, index=True)
    domain = fields.Char(string='Condition Domain', default='[]')
    state_field = fields.Char(string='State Field', default='state')
    state_value = fields.Char(string='State Value')
    account_id = fields.Many2one('rn.whatsapp.account', required=True, ondelete='restrict')
    template_id = fields.Many2one('rn.whatsapp.template', required=True, ondelete='restrict')
    delay_minutes = fields.Integer(string='Delay (minutes)', default=0)
    phone_field = fields.Char(
        string='Phone Field Path',
        default='partner_id.mobile',
        help='Dot path on the record to resolve recipient phone.',
    )
    partner_field = fields.Char(string='Partner Field', default='partner_id')
    company_id = fields.Many2one(
        'res.company',
        required=True,
        default=lambda self: self.env.company,
        index=True,
    )
    note = fields.Text()

    def action_test_rule(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Automation',
                'message': 'Rule "%s" is active for trigger %s.' % (self.name, self.trigger),
                'type': 'info',
                'sticky': False,
            },
        }
