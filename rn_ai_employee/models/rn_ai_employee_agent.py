# -*- coding: utf-8 -*-
"""Domain agents: Sales AI, Finance AI, Executive AI scoped skill packs."""

from __future__ import annotations

from odoo import _, api, fields, models


class AiEmployeeAgent(models.Model):
    _name = 'rn.ai.employee.agent'
    _description = 'AI Copilot Domain Agent'
    _order = 'sequence, name'

    name = fields.Char(required=True, translate=True)
    code = fields.Char(
        required=True,
        index=True,
        help='Stable technical key, e.g. sales, finance, executive.',
    )
    tagline = fields.Char(translate=True)
    focus_label = fields.Char(
        string='Focus',
        translate=True,
        help='Short label shown when routing fails, e.g. sales and CRM.',
    )
    description = fields.Text(translate=True)
    system_prompt = fields.Text(
        string='Agent Persona',
        translate=True,
        help='Optional persona injected into chat and LLM routing.',
    )
    color = fields.Integer(string='Color Index', default=4)
    icon = fields.Selection(
        selection=[
            ('fa-line-chart', 'Chart'),
            ('fa-money', 'Finance'),
            ('fa-briefcase', 'Executive'),
            ('fa-shopping-cart', 'Sales'),
        ],
        default='fa-line-chart',
        required=True,
    )
    active = fields.Boolean(default=True)
    sequence = fields.Integer(default=10)
    tool_ids = fields.Many2many(
        'rn.ai.employee.tool',
        'rn_ai_employee_agent_tool_rel',
        'agent_id',
        'tool_id',
        string='Skills',
    )
    suggestion_ids = fields.Many2many(
        'rn.ai.employee.suggestion',
        'rn_ai_employee_agent_suggestion_rel',
        'agent_id',
        'suggestion_id',
        string='Suggested Questions',
    )
    tool_count = fields.Integer(compute='_compute_tool_count')
    chat_count = fields.Integer(compute='_compute_chat_count')

    _code_unique = models.Constraint(
        'unique(code)',
        'Agent code must be unique.',
    )

    @api.depends('tool_ids')
    def _compute_tool_count(self):
        for agent in self:
            agent.tool_count = len(agent.tool_ids)

    def _compute_chat_count(self):
        grouped = self.env['rn.ai.employee.chat'].read_group(
            [('agent_id', 'in', self.ids)],
            ['agent_id'],
            ['agent_id'],
        )
        counts = {row['agent_id'][0]: row['agent_id_count'] for row in grouped}
        for agent in self:
            agent.chat_count = counts.get(agent.id, 0)

    def action_open_chat(self):
        """Start a conversation with this domain agent."""
        self.ensure_one()
        chat = self.env['rn.ai.employee.chat'].create({
            'name': self.name,
            'agent_id': self.id,
        })
        return {
            'type': 'ir.actions.act_window',
            'name': self.name,
            'res_model': 'rn.ai.employee.chat',
            'res_id': chat.id,
            'view_mode': 'form',
            'target': 'current',
        }

    def action_view_chats(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Conversations'),
            'res_model': 'rn.ai.employee.chat',
            'view_mode': 'list,form',
            'domain': [('agent_id', '=', self.id)],
            'context': {'default_agent_id': self.id},
        }

    @api.model
    def get_default_agent(self):
        """Default systray agent: Sales AI when installed."""
        return self.search([('code', '=', 'sales'), ('active', '=', True)], limit=1)

    @api.model
    def serialize_for_widget(self, agents):
        """JSON payload for systray agent picker."""
        return [{
            'id': agent.id,
            'code': agent.code,
            'name': agent.name,
            'tagline': agent.tagline or '',
            'icon': agent.icon,
            'color': agent.color,
        } for agent in agents]
