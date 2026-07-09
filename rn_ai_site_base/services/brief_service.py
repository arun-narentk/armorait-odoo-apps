# -*- coding: utf-8 -*-
"""Business brief analysis."""

import logging
import re
from collections import Counter

from odoo import models

_logger = logging.getLogger(__name__)

STOPWORDS = {
    'a', 'an', 'the', 'and', 'or', 'in', 'on', 'at', 'to', 'for', 'of', 'we', 'our',
    'is', 'are', 'with', 'from', 'that', 'this', 'it', 'as', 'be', 'by', 'have', 'has',
}

AUDIENCE_BY_TYPE = {
    'bakery': 'Families, event planners, and wedding customers',
    'salon': 'Local residents seeking grooming and beauty services',
    'restaurant': 'Diners, families, and food lovers in the area',
    'tuition': 'Students and parents looking for quality coaching',
    'gym': 'Fitness enthusiasts and health-conscious professionals',
    'clinic': 'Patients seeking trusted local healthcare',
    'hotel': 'Travelers, business guests, and event hosts',
    'other': 'Local customers searching for reliable services online',
}


class RnAiSiteBriefService(models.AbstractModel):
    """Extract keywords and audience from a business brief."""

    _name = 'rn.ai.site.brief.service'
    _description = 'AI Site Brief Service'

    def analyze_brief(self, brief):
        text = ' '.join(filter(None, [
            brief.business_name or '',
            brief.description or '',
            brief.services or '',
            brief.location or '',
        ]))
        keywords = self._extract_keywords(text, brief.business_type)
        if brief.location:
            keywords = [brief.location] + [k for k in keywords if k.lower() != brief.location.lower()]
        return {
            'keywords': keywords[:12],
            'target_audience': AUDIENCE_BY_TYPE.get(brief.business_type, AUDIENCE_BY_TYPE['other']),
        }

    def _extract_keywords(self, text, business_type):
        tokens = re.findall(r'[A-Za-z]{3,}', text.lower())
        filtered = [t for t in tokens if t not in STOPWORDS]
        counts = Counter(filtered)
        ranked = [word for word, _ in counts.most_common(8)]
        if business_type and business_type != 'other':
            ranked.insert(0, business_type.replace('_', ' '))
        return ranked

    def ensure_default_settings(self, company_id=None):
        company_id = company_id or self.env.company.id
        Settings = self.env['rn.ai.site.settings']
        settings = Settings.search([('company_id', '=', company_id)], limit=1)
        if not settings:
            settings = Settings.create({
                'name': 'AI Site Settings',
                'company_id': company_id,
            })
        return settings
