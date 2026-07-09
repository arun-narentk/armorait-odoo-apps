# -*- coding: utf-8 -*-
"""Bot definition bound to connectors."""

from odoo import api, fields, models
from odoo.exceptions import ValidationError


class RnMessagingBot(models.Model):
    _name = 'rn.messaging.bot'
    _description = 'Messaging Bot'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'name'

    name = fields.Char(required=True, tracking=True)
    active = fields.Boolean(default=True)
    company_id = fields.Many2one(
        'res.company',
        default=lambda self: self.env.company,
    )
    description = fields.Text()
    welcome_text = fields.Text(
        default='Hello! How can we help you today?',
    )
    node_ids = fields.One2many('rn.messaging.bot.node', 'bot_id')
    start_node_id = fields.Many2one(
        'rn.messaging.bot.node',
        string='Start Node',
        domain="[('bot_id', '=', id)]",
    )
    connector_ids = fields.One2many('rn.messaging.connector', 'bot_id')
    session_count = fields.Integer(compute='_compute_session_count')

    @api.depends('node_ids')
    def _compute_session_count(self):
        grouped = self.env['rn.messaging.bot.session'].read_group(
            [('bot_id', 'in', self.ids)],
            ['bot_id'],
            ['bot_id'],
        )
        counts = {row['bot_id'][0]: row['bot_id_count'] for row in grouped}
        for bot in self:
            bot.session_count = counts.get(bot.id, 0)

    @api.constrains('start_node_id', 'node_ids')
    def _check_start_node(self):
        for bot in self:
            if bot.start_node_id and bot.start_node_id.bot_id != bot:
                raise ValidationError('Start node must belong to this bot.')

    def action_open_nodes(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Bot Nodes',
            'res_model': 'rn.messaging.bot.node',
            'view_mode': 'list,form',
            'domain': [('bot_id', '=', self.id)],
            'context': {'default_bot_id': self.id},
        }

    def action_open_flow_designer(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.client',
            'tag': 'rn_messaging_bot.flow_designer',
            'params': {'bot_id': self.id},
        }

    def get_designer_data(self, bot_id):
        bot = self.browse(bot_id)
        if not bot.exists():
            return {}
        nodes = []
        for node in bot.node_ids.sorted('sequence'):
            nodes.append({
                'id': node.id,
                'name': node.name,
                'node_type': node.node_type,
                'body_text': node.body_text or '',
                'sequence': node.sequence,
                'pos_x': node.pos_x,
                'pos_y': node.pos_y,
                'next_node_id': node.next_node_id.id or False,
                'fallback_node_id': node.fallback_node_id.id or False,
                'options': [
                    {
                        'id': option.id,
                        'name': option.name,
                        'keyword': option.keyword,
                        'target_node_id': option.target_node_id.id,
                    }
                    for option in node.option_ids.sorted('sequence')
                ],
            })
        edges = []
        for node in bot.node_ids:
            if node.next_node_id:
                edges.append({
                    'source': node.id,
                    'target': node.next_node_id.id,
                    'label': 'next',
                })
            if node.fallback_node_id:
                edges.append({
                    'source': node.id,
                    'target': node.fallback_node_id.id,
                    'label': 'fallback',
                })
            for option in node.option_ids:
                edges.append({
                    'source': node.id,
                    'target': option.target_node_id.id,
                    'label': option.keyword,
                })
        return {
            'bot': {
                'id': bot.id,
                'name': bot.name,
                'start_node_id': bot.start_node_id.id or False,
            },
            'nodes': nodes,
            'edges': edges,
        }

    def save_designer_layout(self, bot_id, layout):
        bot = self.browse(bot_id)
        if not bot.exists():
            return False
        for item in layout or []:
            node = self.env['rn.messaging.bot.node'].browse(item.get('id'))
            if node.exists() and node.bot_id == bot:
                node.write({
                    'pos_x': item.get('pos_x', node.pos_x),
                    'pos_y': item.get('pos_y', node.pos_y),
                })
        return True
