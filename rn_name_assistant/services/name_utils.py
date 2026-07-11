# -*- coding: utf-8 -*-
"""Pure naming helpers for template rendering and cleanup."""

from __future__ import annotations

import re
from typing import Mapping

PLACEHOLDER_RE = re.compile(r'\{([A-Za-z_][A-Za-z0-9_]*)\}')
MULTISPACE_RE = re.compile(r'\s+')
TRAILING_PUNCT_RE = re.compile(r'[,\s._-]+$')
KNOWN_BRANDS = {
    'iphone': 'iPhone',
    'ipad': 'iPad',
    'macbook': 'MacBook',
    'dell': 'Dell',
    'hp': 'HP',
    'lenovo': 'Lenovo',
    'samsung': 'Samsung',
    'ikea': 'IKEA',
}


def normalize_key(key: str) -> str:
    return key.strip().lower().replace(' ', '_')


def apply_template(template: str, values: Mapping[str, str]) -> str:
    """Replace {Placeholder} tokens; skip empty optional values."""

    def _replace(match):
        key = normalize_key(match.group(1))
        value = (values.get(key) or '').strip()
        return value if value else ''

    rendered = PLACEHOLDER_RE.sub(_replace, template or '')
    return cleanup_name(rendered)


def expand_abbreviations(text: str, mapping: Mapping[str, str] | None = None) -> str:
    if not text:
        return ''
    abbrev_map = {k.lower(): v for k, v in (mapping or {}).items()}
    words = text.split()
    expanded = []
    for word in words:
        bare = word.rstrip('.,')
        suffix = word[len(bare):] if bare != word else ''
        replacement = abbrev_map.get(bare.lower())
        expanded.append((replacement or word) + suffix)
    return ' '.join(expanded)


def remove_duplicate_words(text: str) -> str:
    if not text:
        return ''
    words = text.split()
    cleaned = []
    prev = None
    for word in words:
        key = word.lower()
        if key == prev:
            continue
        cleaned.append(word)
        prev = key
    return ' '.join(cleaned)


def smart_title_word(word: str) -> str:
    if not word:
        return word
    lower = word.lower()
    if lower in KNOWN_BRANDS:
        return KNOWN_BRANDS[lower]
    if word.isupper() and len(word) <= 4:
        return word
    if any(ch.isdigit() for ch in word):
        return word.upper() if word.isalpha() else word
    return word[:1].upper() + word[1:].lower() if len(word) > 1 else word.upper()


def title_case_smart(text: str) -> str:
    if not text:
        return ''
    return ' '.join(smart_title_word(part) for part in text.split())


def cleanup_name(text: str, abbrev_map: Mapping[str, str] | None = None) -> str:
    if not text:
        return ''
    cleaned = text.replace('__', ' ').replace('--', ' ').replace('..', ' ')
    cleaned = MULTISPACE_RE.sub(' ', cleaned).strip()
    cleaned = TRAILING_PUNCT_RE.sub('', cleaned)
    cleaned = expand_abbreviations(cleaned, abbrev_map)
    cleaned = remove_duplicate_words(cleaned)
    cleaned = title_case_smart(cleaned)
    return cleaned.strip()


def score_name(name: str, seed: str = '', field_count: int = 0) -> float:
    """Rank suggestions: longer structured names score higher than bare seeds."""

    if not name:
        return 0.0
    score = min(len(name), 80) * 0.4
    score += field_count * 8.0
    if seed and seed.lower() not in name.lower():
        score -= 10.0
    if len(name.split()) >= 3:
        score += 12.0
    return max(score, 1.0)
