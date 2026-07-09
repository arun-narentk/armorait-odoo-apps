# -*- coding: utf-8 -*-
"""Mixin to launch AI email compose from business documents."""

from odoo import models


class RnAiEmailMixin(models.AbstractModel):
    _name = 'rn.ai.email.mixin'
    _description = 'AI Email Mixin'

    def action_compose_ai_email(self):
        self.ensure_one()
        partner = False
        if hasattr(self, 'partner_id'):
            partner = self.partner_id
        elif self._name == 'res.partner':
            partner = self
        return {
            'type': 'ir.actions.act_window',
            'name': 'Compose AI Email',
            'res_model': 'rn.ai.email.compose.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_res_model': self._name,
                'default_res_id': self.id,
                'default_partner_id': partner.id if partner else False,
            },
        }
