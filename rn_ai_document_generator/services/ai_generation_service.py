# -*- coding: utf-8 -*-
"""AI content generation with built-in drafts and optional HTTP provider."""

import json
import logging
import urllib.error
import urllib.request

from odoo import models

_logger = logging.getLogger(__name__)


class RnAiDocumentAiGenerationService(models.AbstractModel):
    _name = 'rn.ai.document.ai.generation.service'
    _description = 'AI Document Generation Service'

    def _settings(self, company):
        return self.env['rn.ai.document.settings'].search(
            [('company_id', '=', company.id)], limit=1
        )

    def generate_sections(self, document, context_values=None):
        """Return AI-assisted HTML sections for clause injection."""
        document.ensure_one()
        settings = self._settings(document.company_id)
        provider = settings.ai_provider if settings else 'builtin'
        if provider == 'disabled':
            return {'sections': {}, 'notes': 'AI disabled; template placeholders only.'}
        if provider == 'openai' and settings and settings.ai_api_key:
            return self._generate_openai(document, settings, context_values or {})
        return self._generate_builtin(document, context_values or {})

    def _generate_builtin(self, document, values):
        style = document.style or 'formal'
        lang = document.language or 'en'
        dtype = document.type_id.category if document.type_id else 'custom'
        party = values.get('customer_name') or values.get('employee_name') or values.get('company_name') or 'valued partner'
        company = values.get('company_name') or document.company_id.name

        intros = {
            'formal': 'Dear %s,<br/><br/>We are pleased to present this formal document issued by %s.' % (party, company),
            'corporate': 'Hello %s,<br/><br/>On behalf of %s, please find the details below for your review and action.' % (party, company),
            'legal': 'This document sets forth the terms between %s and %s and should be read carefully.' % (company, party),
            'friendly': 'Hi %s,<br/><br/>Thanks for connecting with %s. Here is your document with everything in one place.' % (party, company),
            'executive': '%s,<br/><br/>Please find a concise executive summary prepared by %s.' % (party, company),
            'technical': 'Document generated for %s by %s. Technical and operational details follow.' % (party, company),
            'marketing': 'Dear %s,<br/><br/>%s is excited to share this tailored document crafted for your needs.' % (party, company),
        }
        scope = {
            'sales': 'Scope covers commercial terms, deliverables, pricing references, and commercial validity where applicable.',
            'hr': 'This HR document covers role intent, employment communication, and organisational policies referenced herein.',
            'legal': 'Scope includes confidentiality, obligations, liability boundaries, and governing process where stated.',
            'finance': 'This finance communication summarises outstanding positions, payment expectations, and reconciliation notes.',
            'purchase': 'Scope covers supply expectations, commercial references, and vendor obligations for the referenced goods/services.',
            'admin': 'This administrative document records authorisation, custody, or access for internal operations.',
            'custom': 'Scope outlines the purpose of this document and the parties referenced within it.',
        }.get(dtype, 'Scope outlines the purpose of this document.')
        terms = {
            'legal': 'Terms are binding upon acceptance. Confidential information must not be disclosed without prior written consent.',
            'hr': 'Employment communications remain confidential. Policies of the company apply unless otherwise amended in writing.',
            'sales': 'Commercial terms remain subject to confirmation. Prices and deliverables apply for the stated validity period.',
            'finance': 'Please settle outstanding amounts as per agreed payment terms to avoid service interruption.',
        }.get(dtype, 'Standard company terms apply unless superseded by a signed agreement.')

        if lang != 'en':
            # Phase 1 keeps English built-in drafts; language flag is stored for later providers
            notes = 'Built-in engine draft in English; connect an AI provider for native %s wording.' % lang
        else:
            notes = 'Generated with built-in draft engine (%s / %s).' % (style, dtype)

        sections = {
            'introduction': intros.get(style, intros['formal']),
            'scope_of_work': scope,
            'terms': terms,
            'closing': 'We appreciate your attention to this document.<br/><br/>Regards,<br/>%s' % company,
        }
        return {'sections': sections, 'notes': notes}

    def _generate_openai(self, document, settings, values):
        prompt = (
            'Write short HTML sections (introduction, scope_of_work, terms, closing) for a %s document. '
            'Tone: %s. Language: %s. Company: %s. Party: %s. Extra: %s. '
            'Return JSON with keys introduction, scope_of_work, terms, closing.'
        ) % (
            document.type_id.name if document.type_id else 'business',
            document.style,
            document.language,
            values.get('company_name') or document.company_id.name,
            values.get('customer_name') or values.get('employee_name') or '',
            (document.template_id.ai_prompt if document.template_id else '') or '',
        )
        url = (settings.ai_api_url or 'https://api.openai.com/v1/chat/completions').rstrip('/')
        payload = {
            'model': settings.ai_model or 'gpt-4o-mini',
            'messages': [
                {'role': 'system', 'content': 'You are a professional business document assistant.'},
                {'role': 'user', 'content': prompt},
            ],
            'temperature': 0.4,
        }
        req = urllib.request.Request(
            url if url.endswith('completions') else url + '/chat/completions',
            data=json.dumps(payload).encode('utf-8'),
            headers={
                'Authorization': 'Bearer %s' % settings.ai_api_key,
                'Content-Type': 'application/json',
            },
            method='POST',
        )
        try:
            with urllib.request.urlopen(req, timeout=45) as resp:
                raw = json.loads(resp.read().decode('utf-8'))
            content = raw['choices'][0]['message']['content']
            try:
                sections = json.loads(content)
            except (TypeError, ValueError):
                sections = {'introduction': content, 'scope_of_work': '', 'terms': '', 'closing': ''}
            return {'sections': sections, 'notes': 'Generated via OpenAI-compatible provider.'}
        except Exception as exc:  # noqa: BLE001
            _logger.warning('AI provider failed, falling back to builtin: %s', exc)
            result = self._generate_builtin(document, values)
            result['notes'] = 'AI provider failed (%s); used built-in draft.' % exc
            return result

    def inject_sections(self, html, sections):
        html = html or ''
        for key, value in (sections or {}).items():
            token = '{{ai_%s}}' % key
            html = html.replace(token, value or '')
            html = html.replace('{{ ai_%s }}' % key, value or '')
        # If template has no AI tokens, append drafting block once
        if sections and 'ai_introduction' not in html and '{{ai_' not in (html or ''):
            block = '<hr/><h3>AI Draft</h3>'
            for key in ('introduction', 'scope_of_work', 'terms', 'closing'):
                if sections.get(key):
                    block += '<p>%s</p>' % sections[key]
            html = (html or '') + block
        return html
