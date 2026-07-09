# -*- coding: utf-8 -*-
"""Resolve connector drivers and send outbound messages."""

from __future__ import annotations

import logging

from odoo import _, api, models
from odoo.exceptions import UserError

from ..connectors.facebook_messenger import FacebookMessengerConnector
from ..connectors.instagram_dm import InstagramDmConnector
from ..connectors.simulation import SimulationConnector
from ..connectors.whatsapp_cloud import WhatsappCloudConnector

_logger = logging.getLogger(__name__)


class RnMessagingConnectorService(models.AbstractModel):
    _name = 'rn.messaging.connector.service'
    _description = 'Messaging Connector Service'

    @api.model
    def _registry(self):
        return {
            'whatsapp': WhatsappCloudConnector(),
            'instagram': InstagramDmConnector(),
            'facebook': FacebookMessengerConnector(),
            'livechat': SimulationConnector(),
        }

    @api.model
    def get_driver(self, connector):
        driver = self._registry().get(connector.channel_type)
        if not driver:
            raise UserError(_('Unsupported channel type: %s') % connector.channel_type)
        return driver

    @api.model
    def send_text(self, conversation, text: str, *, use_queue: bool = True):
        queue = self.env['rn.messaging.queue.service']
        message = queue.enqueue_text(conversation, text)
        if use_queue:
            queue.deliver_message(message)
        return message
