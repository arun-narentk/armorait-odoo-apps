# -*- coding: utf-8 -*-
"""String similarity helpers for duplicate detection."""

from __future__ import annotations

import re
from difflib import SequenceMatcher


def normalize_text(value: str | None) -> str:
    if not value:
        return ''
    return re.sub(r'\s+', ' ', str(value).strip().lower())


def normalize_phone(value: str | None) -> str:
    if not value:
        return ''
    return re.sub(r'\D+', '', str(value))


def compare_values(left, right, match_type: str) -> float:
    """Return similarity score between 0 and 100."""
    if left in (False, None, '') or right in (False, None, ''):
        return 0.0
    if match_type == 'phone':
        left_norm = normalize_phone(left)
        right_norm = normalize_phone(right)
        if not left_norm or not right_norm:
            return 0.0
        return 100.0 if left_norm == right_norm else 0.0
    left_norm = normalize_text(left)
    right_norm = normalize_text(right)
    if not left_norm or not right_norm:
        return 0.0
    if match_type == 'exact':
        return 100.0 if left_norm == right_norm else 0.0
    return SequenceMatcher(None, left_norm, right_norm).ratio() * 100.0


def weighted_score(field_scores: list[tuple[float, float]]) -> float:
    total_weight = sum(weight for _, weight in field_scores)
    if total_weight <= 0:
        return 0.0
    return sum(score * weight for score, weight in field_scores) / total_weight
