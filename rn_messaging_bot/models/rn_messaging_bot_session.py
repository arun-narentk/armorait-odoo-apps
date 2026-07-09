# -*- coding: utf-8 -*-
"""Active bot session state per conversation."""

from odoo import fields, models


class RnMessagingBotSession(models.Model):
    _name = 'rn.messaging.bot.session'
    _description = 'Messaging Bot Session'
    _order = 'id desc'

    name = fields.Char(required=True)
    bot_id = fields.Many2one('rn.messaging.bot', required=True, ondelete='cascade', index=True)
    conversation_id = fields.Many2one(
        'rn.messaging.conversation',
        required=True,
        ondelete='cascade',
        index=True,
    )
    company_id = fields.Many2one(related='conversation_id.company_id', store=True)
    current_node_id = fields.Many2one('rn.messaging.bot.node', ondelete='set null')
    state = fields.Selection(
        selection=[
            ('running', 'Running'),
            ('completed', 'Completed'),
            ('handoff', 'Handed Off'),
        ],
        default='running',
    )
