# -*- coding: utf-8 -*-
"""Bot flow nodes (threads) with branching."""

from odoo import api, fields, models
from odoo.exceptions import ValidationError


class RnMessagingBotNode(models.Model):
    _name = 'rn.messaging.bot.node'
    _description = 'Messaging Bot Node'
    _order = 'sequence, id'

    name = fields.Char(required=True)
    bot_id = fields.Many2one(
        'rn.messaging.bot',
        required=True,
        ondelete='cascade',
        index=True,
    )
    company_id = fields.Many2one(related='bot_id.company_id', store=True)
    sequence = fields.Integer(default=10)
    pos_x = fields.Float(string='Designer X', default=40.0)
    pos_y = fields.Float(string='Designer Y', default=40.0)
    node_type = fields.Selection(
        selection=[
            ('message', 'Send Message'),
            ('menu', 'Menu Options'),
            ('action', 'Run Action'),
            ('handoff', 'Handoff to Agent'),
        ],
        required=True,
        default='message',
    )
    body_text = fields.Text(string='Message Text')
    option_ids = fields.One2many('rn.messaging.bot.node.option', 'node_id')
    action_code = fields.Selection(
        selection=[
            ('create_lead', 'Create CRM Lead'),
            ('noop', 'No Action'),
        ],
        default='noop',
    )
    next_node_id = fields.Many2one(
        'rn.messaging.bot.node',
        string='Next Node',
        domain="[('bot_id', '=', bot_id), ('id', '!=', id)]",
    )
    fallback_node_id = fields.Many2one(
        'rn.messaging.bot.node',
        string='Fallback Node',
        domain="[('bot_id', '=', bot_id), ('id', '!=', id)]",
    )

    @api.constrains('next_node_id', 'fallback_node_id', 'bot_id')
    def _check_node_bot(self):
        for node in self:
            for linked in (node.next_node_id, node.fallback_node_id):
                if linked and linked.bot_id != node.bot_id:
                    raise ValidationError('Linked nodes must belong to the same bot.')


class RnMessagingBotNodeOption(models.Model):
    _name = 'rn.messaging.bot.node.option'
    _description = 'Messaging Bot Menu Option'
    _order = 'sequence, id'

    name = fields.Char(required=True, string='Label')
    keyword = fields.Char(
        required=True,
        help='Match inbound text case-insensitively. Use * for any input.',
    )
    node_id = fields.Many2one(
        'rn.messaging.bot.node',
        required=True,
        ondelete='cascade',
        index=True,
    )
    bot_id = fields.Many2one(related='node_id.bot_id', store=True)
    target_node_id = fields.Many2one(
        'rn.messaging.bot.node',
        string='Go To Node',
        required=True,
        domain="[('bot_id', '=', bot_id)]",
    )
    sequence = fields.Integer(default=10)

    @api.constrains('target_node_id', 'node_id')
    def _check_target_bot(self):
        for option in self:
            if option.target_node_id.bot_id != option.node_id.bot_id:
                raise ValidationError('Option target must belong to the same bot.')
