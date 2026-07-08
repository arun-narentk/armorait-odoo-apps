# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import base64
import json
import logging
import re
from datetime import datetime
from io import BytesIO

from odoo import api, fields, models, _
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

RESUME_EXTRACT_PROMPT = """
Extract the following information from this resume text.
Return ONLY valid JSON, no markdown or explanation.

Required fields (use null if not found):
- full_name (string)
- email (string)
- phone (string)
- skills (list of strings, e.g. ["Python", "Odoo", "PostgreSQL"])
- education (list of objects: degree, institute, year)
- work_experience (list of objects: company, role, start_date, end_date - dates as YYYY-MM or YYYY)
- total_experience_years (number, optional - can be computed from work_experience)

Resume text:
---
{resume_text}
---
"""


class ResumeAiParserService(models.AbstractModel):
    _name = 'resume.ai.parser.service'
    _description = 'Resume AI Parser Service'

    def extract_pdf_text(self, attachment):
        """Extract raw text from PDF using pdfminer.six.
        Returns (text, error_message). error_message is set when file is not a valid PDF.
        """
        if not attachment or attachment.mimetype != 'application/pdf':
            return '', _('Attachment is not a PDF.')
        try:
            raw = attachment.raw
            if not raw:
                return '', _('Attachment is empty.')
            data = base64.b64decode(raw)
            if not data or len(data) < 8:
                _logger.warning("PDF text extraction failed: attachment empty or too small")
                return '', _('File is too small or empty.')
            # PDF files start with %PDF-; reject clearly non-PDF content
            if not data.startswith(b'%PDF'):
                _logger.warning(
                    "PDF text extraction failed: file is not a valid PDF (wrong format or extension). "
                    "Attachment: %s (id=%s)",
                    attachment.name, attachment.id,
                )
                return '', _(
                    'File is not a valid PDF (wrong format or extension). '
                    'Re-save the document as PDF (e.g. Print → Save as PDF) or upload a different file.'
                )
            from pdfminer.high_level import extract_text_to_fp
            from pdfminer.layout import LAParams
            buffer = BytesIO(data)
            out = BytesIO()
            extract_text_to_fp(buffer, out, laparams=LAParams(), output_type='text')
            return out.getvalue().decode('utf-8', errors='replace'), None
        except ImportError:
            _logger.warning("pdfminer.six not installed; cannot extract PDF text")
            return '', _('PDF extraction is not available (pdfminer.six not installed).')
        except Exception as e:
            err_msg = str(e).strip()
            if '/Root' in err_msg or 'not a PDF' in err_msg.lower() or 'invalid' in err_msg.lower():
                _logger.warning(
                    "PDF text extraction failed: file is not a valid or supported PDF (%s). "
                    "Attachment: %s (id=%s)",
                    err_msg[:80], getattr(attachment, 'name', '?'), getattr(attachment, 'id', '?'),
                )
                return '', _(
                    'File is not a valid or supported PDF. '
                    'Re-save as PDF or try a different file.'
                )
            _logger.exception("PDF text extraction failed: %s", e)
            return '', _('Could not extract text from PDF.')

    def parse_resume_with_ai(self, resume_text):
        """Send resume text to AI and return validated JSON. Override in custom module for OpenAI/Azure/local LLM."""
        # Default: no external AI; return minimal structure so flow still works
        # Implementations should use ir.config_parameter or system parameter for API keys
        try:
            result = self._call_ai_provider(resume_text)
            if result:
                return self._validate_parsed_schema(result)
        except Exception as e:
            _logger.exception("AI parse failed: %s", e)
        return None

    def _call_ai_provider(self, resume_text):
        """Override in a connector module (e.g. openai, azure). Return dict or None."""
        # Placeholder: could call requests to OpenAI/Azure/local endpoint
        return None

    def _validate_parsed_schema(self, data):
        """Ensure required keys exist and types are safe."""
        if not isinstance(data, dict):
            return None
        out = {
            'full_name': data.get('full_name') if isinstance(data.get('full_name'), str) else None,
            'email': data.get('email') if isinstance(data.get('email'), str) else None,
            'phone': data.get('phone') if isinstance(data.get('phone'), str) else None,
            'skills': data.get('skills') if isinstance(data.get('skills'), list) else [],
            'education': data.get('education') if isinstance(data.get('education'), list) else [],
            'work_experience': data.get('work_experience') if isinstance(data.get('work_experience'), list) else [],
            'total_experience_years': data.get('total_experience_years') if isinstance(data.get('total_experience_years'), (int, float)) else None,
            'confidence': data.get('confidence') if isinstance(data.get('confidence'), (int, float)) else None,
        }
        out['skills'] = [s for s in out['skills'] if isinstance(s, str)][:200]
        return out

    def normalize_skills(self, env, parsed_skills):
        """Map parsed skill strings to hr.skill IDs. Optionally create missing skills if setting enabled."""
        if not parsed_skills:
            return []
        HrSkill = env['hr.skill']
        Mapping = env['hr.resume.skill.normalization'].sudo()
        auto_create = env['ir.config_parameter'].sudo().get_param(
            'rn_hr_resume_ai_parser.auto_create_skills', 'False'
        ) == 'True'
        mapping_map = {}
        for m in Mapping.search([]):
            key = (m.parsed_name or '').strip().lower()
            if key and m.skill_id:
                mapping_map[key] = m.skill_id.id
        for skill in HrSkill.search([]):
            key = (skill.name or '').strip().lower()
            if key and key not in mapping_map:
                mapping_map[key] = skill.id
        result = []
        default_skill_type = env.ref(
            'rn_hr_resume_ai_parser.hr_skill_type_resume_technical',
            raise_if_not_found=False,
        ) or env['hr.skill.type'].search([], limit=1)
        for name in parsed_skills:
            if not isinstance(name, str) or not name.strip():
                continue
            key = name.strip().lower()
            clean_name = name.strip()[:64]
            sid = mapping_map.get(key)
            if sid and sid not in result:
                result.append(sid)
                continue
            found = HrSkill.search([('name', 'ilike', clean_name)], limit=1)
            if found and found.id not in result:
                result.append(found.id)
                mapping_map[key] = found.id
                continue
            if auto_create and default_skill_type:
                new_skill = HrSkill.create({
                    'name': clean_name,
                    'skill_type_id': default_skill_type.id,
                })
                result.append(new_skill.id)
                mapping_map[key] = new_skill.id
        return result

    def compute_experience_years(self, parsed):
        """Compute total experience in years from work_experience or use AI total_experience_years."""
        if parsed.get('total_experience_years') is not None and isinstance(parsed['total_experience_years'], (int, float)):
            return float(parsed['total_experience_years'])
        total = 0.0
        for exp in parsed.get('work_experience') or []:
            if not isinstance(exp, dict):
                continue
            start = exp.get('start_date') or exp.get('start')
            end = exp.get('end_date') or exp.get('end') or datetime.now().strftime('%Y-%m')
            if not start:
                continue
            try:
                start_dt = self._parse_date(start)
                end_dt = self._parse_date(end) if end else datetime.now()
                if start_dt and end_dt and end_dt >= start_dt:
                    total += (end_dt - start_dt).days / 365.25
            except Exception:
                pass
        return round(total, 2)

    def _parse_date(self, value):
        if not value:
            return None
        if isinstance(value, datetime):
            return value
        if isinstance(value, str):
            for fmt in ('%Y-%m-%d', '%Y-%m', '%Y'):
                try:
                    return datetime.strptime(value.strip()[:10], fmt)
                except ValueError:
                    continue
        return None


class HrResumeSkillNormalization(models.Model):
    _name = 'hr.resume.skill.normalization'
    _description = 'Resume Skill Normalization Mapping'

    parsed_name = fields.Char('Parsed name (e.g. JS, ODOO)', required=True)
    skill_id = fields.Many2one('hr.skill', 'Normalized skill', required=True, ondelete='cascade')

    _sql_constraints = [
        ('parsed_name_unique', 'unique(parsed_name)', 'Parsed name must be unique.'),
    ]
