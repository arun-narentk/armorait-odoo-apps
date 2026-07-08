# -*- coding: utf-8 -*-
"""Send message wizard."""

from odoo import fields, models


class RnWhatsappSendMessageWizard(models.TransientModel):
    """Compose and queue a WhatsApp message from any integrated document."""

    _name = 'rn.whatsapp.send.message.wizard'
    _description = 'Send WhatsApp Message'

    account_id = fields.Many2one('rn.whatsapp.account', string='Account', required=True)
    partner_id = fields.Many2one('res.partner', string='Partner')
    phone = fields.Char(string='Phone', required=True)
    body = fields.Text(string='Message')
    template_id = fields.Many2one('rn.whatsapp.template', string='Template')
    res_model = fields.Char()
    res_id = fields.Integer()

    def action_send(self):
        """Create a draft message and queue it for delivery."""
        self.ensure_one()
        message = self.env['rn.whatsapp.message.service'].build_text_message(
            self.account_id,
            self.phone,
            self.body,
            partner=self.partner_id,
        )
        if self.res_model and self.res_id:
            message.write({'res_model': self.res_model, 'res_id': self.res_id})
        message.action_queue_message()
        return {'type': 'ir.actions.act_window_close'}
