# -*- coding: utf-8 -*-
"""Structured tool output consumed by explainers and action cards."""

from __future__ import annotations

from typing import Any


def tool_result(
    headline: str,
    summary: str,
    *,
    model: str | None = None,
    domain: list | None = None,
    record_ids: list[int] | None = None,
    metrics: list[dict[str, Any]] | None = None,
    lines: list[dict[str, Any]] | None = None,
    category: str = '',
) -> dict[str, Any]:
    """Build a normalized analytics payload. Business logic lives in tools only."""
    result = {
        'headline': headline,
        'summary': summary,
        'category': category,
        'model': model,
        'domain': domain or [],
        'record_ids': record_ids or [],
        'metrics': metrics or [],
        'lines': lines or [],
    }
    result['suggested_actions'] = _default_actions(result)
    return result


def error_result(message: str) -> dict[str, Any]:
    return {'error': message, 'headline': message, 'summary': message}


def _default_actions(result: dict[str, Any]) -> list[dict[str, Any]]:
    actions = []
    if result.get('model') and (result.get('domain') or result.get('record_ids')):
        actions.append({
            'label': 'Open List',
            'action_type': 'open_list',
            'res_model': result['model'],
            'domain': result.get('domain') or [],
            'res_ids': result.get('record_ids') or [],
        })
        actions.append({
            'label': 'Create Activity',
            'action_type': 'create_activity',
            'res_model': result['model'],
            'res_ids': result.get('record_ids') or [],
        })
    return actions


def write_result(
    headline: str,
    summary: str,
    *,
    model: str,
    record_ids: list[int] | None = None,
    category: str = '',
    open_label: str | None = None,
) -> dict[str, Any]:
    """Structured payload for write tools with a primary open-form action."""
    record_ids = record_ids or []
    result = {
        'headline': headline,
        'summary': summary,
        'category': category,
        'model': model,
        'domain': [('id', 'in', record_ids)] if record_ids else [],
        'record_ids': record_ids,
        'metrics': [],
        'lines': [],
        'write_action': True,
    }
    actions = []
    if record_ids:
        actions.append({
            'label': open_label or 'Open Record',
            'action_type': 'open_form',
            'res_model': model,
            'res_ids': record_ids[:1],
        })
        actions.append({
            'label': 'Open List',
            'action_type': 'open_list',
            'res_model': model,
            'domain': [('id', 'in', record_ids)],
            'res_ids': record_ids,
        })
    result['suggested_actions'] = actions
    return result
