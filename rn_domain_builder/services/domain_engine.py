# -*- coding: utf-8 -*-
"""Pure Python natural-language to Odoo domain parser."""

from __future__ import annotations

import re
import calendar
from dataclasses import dataclass, field
from datetime import date, timedelta
from typing import Any

from ..constants import DATE_EXPRESSIONS, LOGICAL_ALIASES, OPERATOR_ALIASES


@dataclass
class DictionaryEntry:
    trigger: str
    field_name: str
    operator: str
    value: Any
    value_type: str = 'char'


@dataclass
class ParseResult:
    domain: list
    clauses: list[dict] = field(default_factory=list)
    suggestions: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


def _normalize(text: str) -> str:
    lowered = text.lower().strip()
    lowered = re.sub(r'\s+', ' ', lowered)
    return lowered


def _month_end(day: date) -> date:
    last_day = calendar.monthrange(day.year, day.month)[1]
    return day.replace(day=last_day)


def _resolve_date(expression: str, today: date | None = None) -> Any:
    today = today or date.today()
    key = DATE_EXPRESSIONS.get(expression, expression)
    if key == 'today':
        return today.isoformat()
    if key == 'yesterday':
        return (today - timedelta(days=1)).isoformat()
    if key == 'this_week':
        start = today - timedelta(days=today.weekday())
        end = start + timedelta(days=6)
        return [start.isoformat(), end.isoformat()]
    if key == 'last_week':
        end = today - timedelta(days=today.weekday() + 1)
        start = end - timedelta(days=6)
        return [start.isoformat(), end.isoformat()]
    if key == 'this_month':
        start = today.replace(day=1)
        end = _month_end(today)
        return [start.isoformat(), end.isoformat()]
    if key == 'last_month':
        first_this = today.replace(day=1)
        end = first_this - timedelta(days=1)
        start = end.replace(day=1)
        return [start.isoformat(), end.isoformat()]
    if key == 'this_year':
        start = today.replace(month=1, day=1)
        end = today.replace(month=12, day=31)
        return [start.isoformat(), end.isoformat()]
    if key == 'next_month':
        first_this = today.replace(day=1)
        if first_this.month == 12:
            start = first_this.replace(year=first_this.year + 1, month=1)
        else:
            start = first_this.replace(month=first_this.month + 1)
        end = _month_end(start)
        return [start.isoformat(), end.isoformat()]
    return expression


def _tokenize(text: str) -> list[str]:
    normalized = _normalize(text)
    for word, symbol in LOGICAL_ALIASES.items():
        normalized = re.sub(rf'\b{word}\b', f' {symbol} ', normalized)
    normalized = normalized.replace(',', ' and ')
    tokens = [token.strip() for token in normalized.split() if token.strip()]
    return tokens


def _find_operator_phrase(text: str) -> tuple[str | None, str]:
    for operator, aliases in sorted(
        OPERATOR_ALIASES.items(),
        key=lambda item: max(len(alias) for alias in item[1]),
        reverse=True,
    ):
        for alias in sorted(aliases, key=len, reverse=True):
            pattern = rf'\b{re.escape(alias)}\b'
            if re.search(pattern, text):
                cleaned = re.sub(pattern, ' ', text, count=1)
                return operator, cleaned.strip()
    return None, text


def _match_dictionary(text: str, entries: list[DictionaryEntry]) -> tuple[DictionaryEntry | None, str]:
    sorted_entries = sorted(entries, key=lambda entry: len(entry.trigger), reverse=True)
    for entry in sorted_entries:
        pattern = rf'\b{re.escape(entry.trigger)}\b'
        if re.search(pattern, text):
            remainder = re.sub(pattern, ' ', text, count=1).strip()
            return entry, remainder
    return None, text


def _extract_number(text: str) -> tuple[float | None, str]:
    match = re.search(r'(-?\d+(?:\.\d+)?)', text)
    if not match:
        return None, text
    value = float(match.group(1))
    remainder = (text[:match.start()] + text[match.end():]).strip()
    return value, remainder


def _entry_to_leaf(entry: DictionaryEntry, operator: str | None, today: date | None) -> list:
    value = entry.value
    if entry.value_type == 'date_expression' and isinstance(value, str):
        value = _resolve_date(value, today=today)
    op = operator if operator and entry.operator in ('=', '!=', '>', '>=', '<', '<=') else entry.operator
    if isinstance(value, list):
        return [(entry.field_name, '>=', value[0]), (entry.field_name, '<=', value[1])]
    if isinstance(value, list) and op == 'in':
        return [(entry.field_name, 'in', value)]
    return [(entry.field_name, op, value)]


def _parse_clause(
    clause_text: str,
    entries: list[DictionaryEntry],
    today: date | None = None,
) -> tuple[list | None, list[str]]:
    warnings: list[str] = []
    text = _normalize(clause_text)
    if not text:
        return None, warnings

    operator, working = _find_operator_phrase(text)
    leaves: list = []
    used_fields: set[str] = set()
    if operator:
        amount_number, numeric_remainder = _extract_number(working)
        if amount_number is not None:
            for entry in entries:
                if entry.field_name in ('amount_total', 'qty_available'):
                    leaves.append((entry.field_name, operator, amount_number))
                    used_fields.add(entry.field_name)
                    working = numeric_remainder
                    break
    scanned = working or text
    safety = 0
    while scanned and safety < 8:
        safety += 1
        entry, remainder = _match_dictionary(scanned, entries)
        if entry:
            if entry.field_name in used_fields:
                scanned = remainder.strip()
                continue
            leaves.extend(_entry_to_leaf(entry, operator if not leaves else None, today))
            used_fields.add(entry.field_name)
            scanned = remainder.strip()
            continue
        number, remainder = _extract_number(scanned)
        if number is not None:
            entry2, _ = _match_dictionary(remainder, entries)
            if entry2:
                op = operator or '<' if 'below' in text or 'under' in text else operator or '>'
                leaves.extend([(entry2.field_name, op, number)])
                scanned = ''
                continue
        break

    if leaves:
        if len(leaves) == 1:
            return leaves, warnings
        return ['&'] + leaves, warnings

    warnings.append(f'Could not parse clause: {clause_text}')
    return None, warnings


def _split_clauses(text: str) -> list[tuple[str, str]]:
    """Return list of (connector, clause_text). First connector is implicit AND."""
    normalized = _normalize(text)
    parts = re.split(r'\s+(and|or)\s+|\s*[|&]\s*', normalized)
    if len(parts) == 1:
        return [('&', parts[0].strip())]
    result: list[tuple[str, str]] = []
    connector = '&'
    index = 0
    while index < len(parts):
        chunk = parts[index].strip()
        if chunk in ('and', 'or', '&', '|'):
            connector = '|' if chunk in ('or', '|') else '&'
            index += 1
            continue
        if chunk:
            result.append((connector, chunk))
        index += 1
    if not result:
        return [('&', normalized)]
    result[0] = ('&', result[0][1])
    return result


def _combine_domains(parts: list[list]) -> list:
    if not parts:
        return []
    if len(parts) == 1:
        return parts[0]
    domain: list = ['|'] * (len(parts) - 1)
    for part in parts:
        domain.extend(part)
    return domain


def parse_description(
    description: str,
    entries: list[DictionaryEntry],
    suggestion_pool: list[str] | None = None,
    today: date | None = None,
) -> ParseResult:
    """Parse a plain-English filter description into an Odoo domain."""
    text = description.strip()
    if not text:
        return ParseResult(domain=[], suggestions=suggestion_pool or [])

    clause_specs = _split_clauses(text)
    parsed_parts: list[list] = []
    warnings: list[str] = []
    connectors = {connector for connector, _ in clause_specs}

    for connector, clause_text in clause_specs:
        clause_domain, clause_warnings = _parse_clause(clause_text, entries, today=today)
        warnings.extend(clause_warnings)
        if clause_domain:
            parsed_parts.append(clause_domain)

    if not parsed_parts:
        return ParseResult(domain=[], warnings=warnings, suggestions=suggestion_pool or [])

    if '|' in connectors:
        final_domain = _combine_domains(parsed_parts)
    elif len(parsed_parts) > 1:
        merged: list = []
        for part in parsed_parts:
            merged.extend(part)
        final_domain = merged
    else:
        final_domain = parsed_parts[0]

    suggestions = []
    if suggestion_pool:
        lowered = _normalize(text)
        suggestions = [chip for chip in suggestion_pool if chip not in lowered][:8]

    return ParseResult(
        domain=final_domain,
        clauses=[{'text': clause, 'connector': connector} for connector, clause in clause_specs],
        suggestions=suggestions,
        warnings=warnings,
    )
