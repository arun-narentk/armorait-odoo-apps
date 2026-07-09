# -*- coding: utf-8 -*-
"""Mixin to send documents for signature from any model."""

from odoo import fields, models


class RnDocPlatformMixin(models.AbstractModel):
    _name = 'rn.doc.platform.mixin'
    _description = 'Document Platform Mixin'

    sign_request_id = fields.Many2one('rn.doc.sign.request', copy=False)
    sign_state = fields.Selection(related='sign_request_id.state', string='Signature Status', store=True)

    def action_send_for_signature(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Send for Signature',
            'res_model': 'rn.doc.send.signature.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_res_model': self._name,
                'default_res_id': self.id,
                'default_document_name': self.display_name,
            },
        }

    def action_open_sign_request(self):
        self.ensure_one()
        if not self.sign_request_id:
            return False
        return {
            'type': 'ir.actions.act_window',
            'name': 'Sign Request',
            'res_model': 'rn.doc.sign.request',
            'view_mode': 'form',
            'res_id': self.sign_request_id.id,
        }
