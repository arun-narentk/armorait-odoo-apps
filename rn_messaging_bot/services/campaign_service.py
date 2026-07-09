# -*- coding: utf-8 -*-
"""Campaign preparation and broadcast delivery."""

from __future__ import annotations

import logging

from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class RnMessagingCampaignService(models.AbstractModel):
    _name = 'rn.messaging.campaign.service'
    _description = 'Messaging Campaign Service'

    @api.model
    def prepare_lines(self, campaign):
        campaign.ensure_one()
        Line = self.env['rn.messaging.campaign.line']
        existing_partners = set(campaign.line_ids.mapped('partner_id').ids)
        to_create = []
        for partner in campaign.partner_ids:
            if partner.id in existing_partners:
                continue
            external_id = self._resolve_external_contact_id(partner)
            to_create.append({
                'campaign_id': campaign.id,
                'partner_id': partner.id,
                'external_contact_id': external_id,
            })
        if to_create:
            Line.create(to_create)
        return campaign.line_ids

    @api.model
    def send_campaign(self, campaign_id, limit=100):
        campaign = self.env['rn.messaging.campaign'].browse(campaign_id)
        if not campaign.exists():
            return 0
        if campaign.state == 'cancelled':
            return 0
        campaign.write({'state': 'sending'})
        pending = campaign.line_ids.filtered(lambda line: line.state == 'pending')[:limit]
        sent = 0
        for line in pending:
            if self._send_line(line):
                sent += 1
        remaining = campaign.line_ids.filtered(lambda line: line.state == 'pending')
        if remaining:
            campaign.write({'state': 'sending'})
        else:
            campaign.write({'state': 'done'})
        _logger.info('Campaign %s sent %s messages', campaign.id, sent)
        return sent

    @api.model
    def process_scheduled_campaigns(self, limit=5):
        now = fields.Datetime.now()
        campaigns = self.env['rn.messaging.campaign'].search([
            ('state', '=', 'scheduled'),
            '|',
            ('schedule_at', '=', False),
            ('schedule_at', '<=', now),
        ], limit=limit)
        total = 0
        for campaign in campaigns:
            if not campaign.line_ids:
                self.prepare_lines(campaign)
            total += self.send_campaign(campaign.id)
        return total

    @api.model
    def _send_line(self, line):
        campaign = line.campaign_id
        connector = campaign.connector_id
        template = campaign.template_id
        conversation = self._get_or_create_conversation(line, connector)
        body = template.render_body(partner=line.partner_id, conversation=conversation)
        message = self.env['rn.messaging.connector.service'].send_text(
            conversation,
            body,
        )
        if message.delivery_state == 'sent':
            line.write({
                'state': 'sent',
                'conversation_id': conversation.id,
                'message_id': message.id,
                'error_message': False,
            })
            return True
        line.write({
            'state': 'failed',
            'conversation_id': conversation.id,
            'message_id': message.id,
            'error_message': message.error_message,
        })
        return False

    @api.model
    def _get_or_create_conversation(self, line, connector):
        Conversation = self.env['rn.messaging.conversation']
        external_id = line.external_contact_id or self._resolve_external_contact_id(line.partner_id)
        conversation = Conversation.search([
            ('connector_id', '=', connector.id),
            ('partner_id', '=', line.partner_id.id),
            ('state', '!=', 'closed'),
        ], limit=1)
        if conversation:
            return conversation
        return Conversation.create({
            'name': line.partner_id.name,
            'connector_id': connector.id,
            'partner_id': line.partner_id.id,
            'external_contact_id': external_id,
            'state': 'human',
        })

    @api.model
    def _resolve_external_contact_id(self, partner):
        if partner.rn_messaging_external_ids:
            return partner.rn_messaging_external_ids.split(',')[0].strip()
        phone = (partner.phone or '').replace(' ', '').replace('+', '')
        return phone or str(partner.id)
