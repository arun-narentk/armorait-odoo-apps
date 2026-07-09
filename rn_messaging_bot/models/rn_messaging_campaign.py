# -*- coding: utf-8 -*-
"""Broadcast campaigns to contacts via messaging connectors."""

from odoo import api, fields, models
from odoo.exceptions import UserError


class RnMessagingCampaign(models.Model):
    _name = 'rn.messaging.campaign'
    _description = 'Messaging Campaign'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'id desc'

    name = fields.Char(required=True, tracking=True)
    active = fields.Boolean(default=True)
    company_id = fields.Many2one(
        'res.company',
        required=True,
        default=lambda self: self.env.company,
    )
    connector_id = fields.Many2one(
        'rn.messaging.connector',
        required=True,
        domain="[('company_id', '=', company_id)]",
        tracking=True,
    )
    template_id = fields.Many2one(
        'rn.messaging.template',
        required=True,
        domain="['|', ('connector_id', '=', False), ('connector_id', '=', connector_id)]",
    )
    partner_ids = fields.Many2many(
        'res.partner',
        'rn_messaging_campaign_partner_rel',
        'campaign_id',
        'partner_id',
        string='Recipients',
    )
    schedule_at = fields.Datetime(string='Schedule At')
    state = fields.Selection(
        selection=[
            ('draft', 'Draft'),
            ('scheduled', 'Scheduled'),
            ('sending', 'Sending'),
            ('done', 'Done'),
            ('cancelled', 'Cancelled'),
        ],
        default='draft',
        tracking=True,
    )
    line_ids = fields.One2many('rn.messaging.campaign.line', 'campaign_id')
    line_count = fields.Integer(compute='_compute_line_stats')
    sent_count = fields.Integer(compute='_compute_line_stats')
    failed_count = fields.Integer(compute='_compute_line_stats')

    @api.depends('line_ids', 'line_ids.state')
    def _compute_line_stats(self):
        for campaign in self:
            lines = campaign.line_ids
            campaign.line_count = len(lines)
            campaign.sent_count = len(lines.filtered(lambda line: line.state == 'sent'))
            campaign.failed_count = len(lines.filtered(lambda line: line.state == 'failed'))

    def action_prepare_recipients(self):
        self.ensure_one()
        if not self.partner_ids:
            raise UserError('Add at least one recipient before preparing the campaign.')
        self.env['rn.messaging.campaign.service'].prepare_lines(self)
        return True

    def action_schedule(self):
        for campaign in self:
            if not campaign.line_ids:
                campaign.action_prepare_recipients()
            campaign.write({'state': 'scheduled'})
        return True

    def action_send_now(self):
        for campaign in self:
            if not campaign.line_ids:
                campaign.action_prepare_recipients()
            self.env['rn.messaging.campaign.service'].send_campaign(campaign.id)
        return True

    def action_cancel(self):
        self.write({'state': 'cancelled'})
        return True

    def action_open_lines(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Campaign Lines',
            'res_model': 'rn.messaging.campaign.line',
            'view_mode': 'list,form',
            'domain': [('campaign_id', '=', self.id)],
            'context': {'default_campaign_id': self.id},
        }


class RnMessagingCampaignLine(models.Model):
    _name = 'rn.messaging.campaign.line'
    _description = 'Messaging Campaign Line'
    _order = 'id'

    campaign_id = fields.Many2one(
        'rn.messaging.campaign',
        required=True,
        ondelete='cascade',
        index=True,
    )
    company_id = fields.Many2one(related='campaign_id.company_id', store=True)
    partner_id = fields.Many2one('res.partner', required=True, index=True)
    external_contact_id = fields.Char(index=True)
    conversation_id = fields.Many2one('rn.messaging.conversation', ondelete='set null')
    message_id = fields.Many2one('rn.messaging.message', ondelete='set null')
    state = fields.Selection(
        selection=[
            ('pending', 'Pending'),
            ('sent', 'Sent'),
            ('failed', 'Failed'),
        ],
        default='pending',
        index=True,
    )
    error_message = fields.Char()
