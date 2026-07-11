# -*- coding: utf-8 -*-
"""Validate generated domains against model metadata."""

from __future__ import annotations

from odoo import _, api, models


class RnDomainValidatorService(models.AbstractModel):
    _name = 'rn.domain.validator.service'
    _description = 'Domain Validator Service'

    @api.model
    def validate(self, res_model: str, domain: list) -> dict:
        errors: list[str] = []
        if res_model not in self.env:
            return {'valid': False, 'errors': [_('Unknown model %s') % res_model]}
        if not isinstance(domain, list):
            return {'valid': False, 'errors': [_('Domain must be a list.')]}
        try:
            self.env[res_model].search_count(domain)
        except Exception as exc:  # noqa: BLE001 - surface parser issues to user
            errors.append(str(exc))
        return {'valid': not errors, 'errors': errors}

    @api.model
    def count_records(self, res_model: str, domain: list) -> int:
        validation = self.validate(res_model, domain)
        if not validation['valid']:
            return 0
        return self.env[res_model].search_count(domain)
