# -*- coding: utf-8 -*-
"""Database registry for AI tools."""

from __future__ import annotations

import json
import logging
from typing import Any

from odoo import _, api, fields, models
from odoo.exceptions import UserError

from ..tools.registry import get_tool_class

_logger = logging.getLogger(__name__)


class AiEmployeeTool(models.Model):
    _name = 'ai.employee.tool'
    _description = 'AI Employee Tool'
    _order = 'name'

    name = fields.Char(required=True, translate=True)
    description = fields.Text(translate=True)
    model_name = fields.Char(
        string='Technical Name',
        required=True,
        help='Python registry key, e.g. overdue_invoices.',
    )
    active = fields.Boolean(default=True)

    _model_name_unique = models.Constraint(
        'unique(model_name)',
        'Technical tool name must be unique.',
    )

    def execute(self, arguments: dict[str, Any] | None = None) -> dict[str, Any]:
        """Execute the linked Python tool class with the current user environment."""
        self.ensure_one()
        return self._execute_tool(self.model_name, arguments or {})

    @api.model
    def execute_by_name(self, technical_name: str, arguments: dict[str, Any] | None = None) -> dict[str, Any]:
        """Execute an active registry record by technical name."""
        tool = self.search([('model_name', '=', technical_name), ('active', '=', True)], limit=1)
        if not tool:
            raise UserError(_('Tool "%s" is not registered or is inactive.') % technical_name)
        return tool.execute(arguments or {})

    @api.model
    def _execute_tool(self, technical_name: str, arguments: dict[str, Any]) -> dict[str, Any]:
        """Dispatch execution to the Python tool class."""
        tool_class = get_tool_class(technical_name)
        if not tool_class:
            raise UserError(_('No Python implementation found for tool "%s".') % technical_name)

        tool_record = self.search([('model_name', '=', technical_name)], limit=1)
        if tool_record:
            tool_record.check_access('read')

        _logger.info('Executing AI tool %s with args=%s', technical_name, arguments)
        try:
            result = tool_class(self.env).execute(arguments)
            _logger.info('AI tool %s completed successfully', technical_name)
            return result
        except Exception as exc:
            _logger.exception('AI tool %s failed', technical_name)
            return {'error': str(exc)}

    @api.model
    def get_openai_definitions(self) -> list[dict[str, Any]]:
        """Return OpenAI function schemas for all active registered tools."""
        definitions = []
        for tool in self.search([('active', '=', True)]):
            tool_class = get_tool_class(tool.model_name)
            if tool_class:
                definitions.append(tool_class(self.env).as_openai_definition())
        return definitions

    def action_test_tool(self):
        """Manual test entry point from the tool form."""
        self.ensure_one()
        result = self.execute({})
        message = json.dumps(result, indent=2, default=str)
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Tool Result'),
                'message': message,
                'sticky': True,
                'type': 'success' if 'error' not in result else 'warning',
            },
        }
