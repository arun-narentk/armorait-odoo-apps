# -*- coding: utf-8 -*-

import re
from urllib.parse import quote

from odoo import _, models


class WhatsAppMixin(models.AbstractModel):
    _name = 'whatsapp.mixin'
    _description = 'WhatsApp shared helpers'

    def _whatsapp_phone_from_partner(self, partner):
        """Get WhatsApp number from partner: mobile preferred (if field exists), then phone. Digits only."""
        if not partner:
            return None
        raw = (getattr(partner, 'mobile', None) or partner.phone or '').strip()
        if not raw:
            return None
        digits = re.sub(r'\D', '', raw)
        if len(digits) < 8:
            return None
        return digits

    def _whatsapp_log_outbound(self, phone, message_body):
        """Post a note on self (must be mail.thread) logging the WhatsApp send. Two-way logging: outbound."""
        self.ensure_one()
        if not hasattr(self, 'message_post'):
            return
        display_phone = '+' + phone if len(phone) <= 15 else phone[:15] + '…'
        intro = _('WhatsApp message sent to %s') % display_phone
        preview = message_body[:400] + ('…' if len(message_body) > 400 else '')
        body = '%s\n\n%s' % (intro, preview)
        self.message_post(body=body, message_type='notification', subtype_xmlid='mail.mt_note')

    def _whatsapp_act_url(self, phone, message):
        """Return ir.actions.act_url to open wa.me with phone and pre-filled text."""
        text_param = quote(message)
        url = 'https://wa.me/%s?text=%s' % (phone, text_param)
        return {
            'type': 'ir.actions.act_url',
            'url': url,
            'target': 'new',
        }
