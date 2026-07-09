# -*- coding: utf-8 -*-
"""Build configured AI providers from system parameters."""

from __future__ import annotations

from typing import TYPE_CHECKING

from odoo.exceptions import UserError

from ..providers.openai_provider import OpenAIProvider

if TYPE_CHECKING:
    from odoo.api import Environment


def get_provider(env: Environment) -> OpenAIProvider:
    """Return the configured provider for the current company environment."""
    icp = env['ir.config_parameter'].sudo()
    provider_code = icp.get_param('rn_ai_employee.provider', 'openai') or 'openai'
    if provider_code != 'openai':
        raise UserError('Only the OpenAI-compatible provider is available in this release.')

    api_key = icp.get_param('rn_ai_employee.api_key', '') or ''
    api_url = icp.get_param('rn_ai_employee.api_url', '') or OpenAIProvider.DEFAULT_API_URL
    model = icp.get_param('rn_ai_employee.model', '') or 'gpt-4o-mini'
    temperature = float(icp.get_param('rn_ai_employee.temperature', '0.2') or 0.2)
    return OpenAIProvider(
        api_key=api_key,
        model=model,
        temperature=temperature,
        api_url=api_url,
    )


def llm_enabled(env: Environment) -> bool:
    """True when LLM routing is enabled and an API key is configured."""
    icp = env['ir.config_parameter'].sudo()
    if icp.get_param('rn_ai_employee.use_llm', 'True') != 'True':
        return False
    return bool(icp.get_param('rn_ai_employee.api_key', ''))
