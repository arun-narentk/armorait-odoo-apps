# -*- coding: utf-8 -*-
"""Odoo 19 helpers: employee contract data lives on hr.version, not hr.contract."""

from __future__ import annotations

from odoo import fields


def running_version_domain(company_id=None, extra=None):
    """Domain for employee versions that are currently in contract."""
    today = fields.Date.today()
    domain = [
        ('employee_id', '!=', False),
        '|',
        ('contract_date_start', '=', False),
        ('contract_date_start', '<=', today),
        '|',
        ('contract_date_end', '=', False),
        ('contract_date_end', '>=', today),
    ]
    if company_id:
        domain.append(('company_id', '=', company_id))
    if extra:
        domain.extend(extra)
    return domain


def search_running_versions(env, company_id=None, extra=None):
    """Return hr.version records representing active employee contracts."""
    return env['hr.version'].search(running_version_domain(company_id, extra))
