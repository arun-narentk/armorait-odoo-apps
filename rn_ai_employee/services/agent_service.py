# -*- coding: utf-8 -*-
"""Domain agent routing: scope skills, suggestions, and LLM context per agent."""

from __future__ import annotations

import logging
from typing import Any

from odoo import _

from ..tools.registry import get_tool_class

_logger = logging.getLogger(__name__)


class AgentService:
    """Resolve which skills an agent may use without duplicating tool logic."""

    def __init__(self, env):
        self.env = env

    def get_chat_agent(self, chat):
        """Return the active domain agent for a chat, if any."""
        if not chat or not chat.agent_id:
            return self.env['rn.ai.employee.agent']
        return chat.agent_id

    def get_allowed_tool_names(self, agent) -> set[str]:
        """Technical tool names this agent may execute."""
        if not agent:
            tools = self.env['rn.ai.employee.tool'].search([('active', '=', True)])
            return set(tools.mapped('model_name'))
        return set(agent.tool_ids.filtered('active').mapped('model_name'))

    def is_tool_allowed(self, agent, tool_name: str) -> bool:
        if not tool_name:
            return False
        return tool_name in self.get_allowed_tool_names(agent)

    def filter_tool_name(self, agent, tool_name: str | None) -> str | None:
        """Drop tool results that are outside the agent skill pack."""
        if tool_name and self.is_tool_allowed(agent, tool_name):
            return tool_name
        if tool_name and agent:
            _logger.info(
                'Agent %s cannot use tool %s; request blocked.',
                agent.code,
                tool_name,
            )
        return None

    def get_openai_definitions(self, agent) -> list[dict[str, Any]]:
        """OpenAI schemas limited to the agent skill pack."""
        Tool = self.env['rn.ai.employee.tool']
        allowed = self.get_allowed_tool_names(agent)
        definitions = []
        for tool in Tool.search([('active', '=', True), ('model_name', 'in', list(allowed))]):
            tool_class = get_tool_class(tool.model_name)
            if tool_class:
                definitions.append(tool_class(self.env).as_openai_definition())
        return definitions

    def get_suggestions(self, agent, limit: int = 6):
        """Starter questions for the active agent."""
        Suggestion = self.env['rn.ai.employee.suggestion']
        domain = [('active', '=', True)]
        if agent and agent.suggestion_ids:
            return agent.suggestion_ids.filtered('active').sorted('sequence')[:limit]
        if agent:
            return Suggestion.search(domain, order='sequence, id', limit=limit)
        return Suggestion.search(domain, order='sequence, id', limit=limit)

    def build_system_prompt(self, agent, product_name: str) -> str:
        """Persona text injected into chat and LLM routing."""
        base = _(
            'You are %(product)s. I answer everyday business questions using live company data. '
            'Pick a suggested question or ask in your own words.'
        ) % {'product': product_name}
        if not agent:
            return base
        persona = (agent.system_prompt or '').strip()
        if persona:
            return f'{persona}\n\n{base}'
        return _(
            '%(persona)s\n\n%(base)s'
        ) % {
            'persona': _('You are %(agent)s, focused on %(focus)s.') % {
                'agent': agent.name,
                'focus': agent.focus_label or agent.name,
            },
            'base': base,
        }

    def agent_not_allowed_message(self, agent) -> str:
        return _(
            'That request is outside %(agent)s skills. Try a question about %(focus)s '
            'or switch to another domain agent.'
        ) % {
            'agent': agent.name,
            'focus': agent.focus_label or _('this domain'),
        }


def get_agent_service(env) -> AgentService:
    return AgentService(env)
