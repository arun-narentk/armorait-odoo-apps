# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import json
import logging
from datetime import datetime

from odoo import api, fields, models, _
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

PARSING_STATUS = [
    ('draft', 'Draft'),
    ('pending', 'Pending'),
    ('processing', 'Processing'),
    ('done', 'Done'),
    ('error', 'Error'),
]


class HrApplicant(models.Model):
    _inherit = 'hr.applicant'

    resume_text = fields.Text(string='Resume Text', readonly=True)
    parsed_json = fields.Json(string='Parsed Data', readonly=True)
    extracted_skill_ids = fields.Many2many(
        'hr.skill',
        'hr_applicant_extracted_skill_rel',
        'applicant_id',
        'skill_id',
        string='Extracted Skills',
        readonly=True,
    )
    total_experience_years = fields.Float(string='Total Experience (Years)', readonly=True)
    match_score = fields.Float(string='Match Score', readonly=True)
    parsing_status = fields.Selection(
        PARSING_STATUS,
        string='Parsing Status',
        default='draft',
        copy=False,
        tracking=True,
    )
    parsing_error_message = fields.Text(string='Parsing Error', readonly=True)
    resume_attachment_id = fields.Many2one(
        'ir.attachment',
        string='Resume Attachment',
        readonly=True,
        copy=False,
    )
    parsing_confidence = fields.Float(
        string='Parsing Confidence',
        readonly=True,
        help='Confidence score 0-100 for parsed data quality.',
    )
    duplicate_applicant_ids = fields.Many2many(
        'hr.applicant',
        'hr_applicant_duplicate_rel',
        'applicant_id',
        'duplicate_id',
        string='Possible duplicates',
        compute='_compute_duplicate_applicant_ids',
        store=False,
        readonly=True,
    )
    duplicate_warning = fields.Char(
        string='Duplicate warning',
        compute='_compute_duplicate_applicant_ids',
        store=False,
        readonly=True,
    )
    duplicate_count = fields.Integer(
        string='Duplicate count',
        compute='_compute_duplicate_applicant_ids',
        store=False,
        readonly=True,
    )
    resume_similarity_ids = fields.One2many(
        'hr.resume.similarity',
        'applicant_id',
        string='Similar resumes',
        readonly=True,
    )
    resume_similarity_count = fields.Integer(
        string='Similar count',
        compute='_compute_resume_similarity_count',
        store=False,
    )

    @api.depends('resume_similarity_ids')
    def _compute_resume_similarity_count(self):
        for applicant in self:
            applicant.resume_similarity_count = len(applicant.resume_similarity_ids)

    @api.depends('email_normalized', 'partner_phone_sanitized')
    def _compute_duplicate_applicant_ids(self):
        for applicant in self:
            duplicates = applicant._find_duplicate_applicants()
            applicant.duplicate_applicant_ids = duplicates
            applicant.duplicate_count = len(duplicates)
            if duplicates:
                applicant.duplicate_warning = _('%s possible duplicate(s) by email/phone.') % len(duplicates)
            else:
                applicant.duplicate_warning = False

    def _find_duplicate_applicants(self):
        """Find other applicants with same email_normalized or partner_phone_sanitized (excluding self)."""
        self.ensure_one()
        if not self.email_normalized and not self.partner_phone_sanitized:
            return self.env['hr.applicant']
        domain = [('id', '!=', self.id), ('active', '=', True)]
        if self.email_normalized and self.partner_phone_sanitized:
            domain = domain + [
                '|',
                ('email_normalized', '=', self.email_normalized),
                ('partner_phone_sanitized', '=', self.partner_phone_sanitized),
            ]
        elif self.email_normalized:
            domain.append(('email_normalized', '=', self.email_normalized))
        else:
            domain.append(('partner_phone_sanitized', '=', self.partner_phone_sanitized))
        return self.search(domain)

    def _get_resume_pdf_attachment(self):
        """Return the first PDF attachment linked to this applicant."""
        self.ensure_one()
        return self.env['ir.attachment'].search([
            ('res_model', '=', 'hr.applicant'),
            ('res_id', '=', self.id),
            ('mimetype', '=', 'application/pdf'),
        ], limit=1, order='id desc')

    def _trigger_resume_parsing(self, attachment=None):
        """Enqueue resume parsing for this applicant. Non-blocking."""
        for applicant in self:
            if applicant.parsing_status in ('processing', 'pending'):
                continue
            att = attachment or applicant._get_resume_pdf_attachment()
            if not att or att.mimetype != 'application/pdf':
                continue
            applicant.write({
                'resume_attachment_id': att.id,
                'parsing_status': 'pending',
            })
            # queue_job: override _trigger_resume_parsing to call applicant.with_delay()._run_resume_parsing()
            # Without queue_job, cron processes records with parsing_status = 'pending'

    def _run_resume_parsing(self):
        """Execute resume parsing (extract PDF, AI parse, normalize, match score)."""
        for applicant in self:
            try:
                applicant._run_resume_parsing_single()
            except Exception as e:
                _logger.exception("Resume parsing failed for applicant %s: %s", applicant.id, e)
                applicant.sudo().write({
                    'parsing_status': 'error',
                    'parsing_error_message': str(e),
                })

    def _run_resume_parsing_single(self):
        self.ensure_one()
        if self.parsing_status not in ('pending', 'draft'):
            return
        self.sudo().parsing_status = 'processing'
        self.sudo().parsing_error_message = False

        attachment = self.resume_attachment_id or self._get_resume_pdf_attachment()
        if not attachment:
            self.sudo().write({
                'parsing_status': 'error',
                'parsing_error_message': _('No PDF attachment found.'),
            })
            return

        parser = self.env['resume.ai.parser.service'].sudo()
        raw_text, extract_error = parser.extract_pdf_text(attachment)
        if not raw_text or not raw_text.strip():
            self.sudo().write({
                'resume_text': '',
                'parsing_status': 'error',
                'parsing_error_message': extract_error or _('Could not extract text from PDF.'),
            })
            return

        parsed = parser.parse_resume_with_ai(raw_text)
        if not parsed:
            self.sudo().write({
                'resume_text': raw_text[:50000],
                'parsing_status': 'error',
                'parsing_error_message': _('AI parsing returned no valid data.'),
            })
            return

        # Normalize skills and experience
        skill_ids = self._normalize_parsed_skills(parsed.get('skills') or [])
        total_years = self._compute_total_experience_years(parsed)

        # Update applicant fields from parsed data (never trust AI blindly)
        vals = {
            'resume_text': raw_text[:50000],
            'parsed_json': parsed,
            'extracted_skill_ids': [(6, 0, skill_ids)],
            'total_experience_years': total_years,
            'parsing_status': 'done',
            'parsing_error_message': False,
        }
        # Optionally fill partner_name, email_from, partner_phone if empty
        if not self.partner_name and parsed.get('full_name'):
            vals['partner_name'] = parsed['full_name'][:256]
        if not self.email_from and parsed.get('email'):
            vals['email_from'] = parsed['email'][:128]
        if not self.partner_phone and parsed.get('phone'):
            vals['partner_phone'] = parsed['phone'][:32]
        # Confidence: from AI or computed from completeness
        confidence = parsed.get('confidence')
        if confidence is not None and isinstance(confidence, (int, float)):
            vals['parsing_confidence'] = min(100.0, max(0.0, float(confidence)))
        else:
            vals['parsing_confidence'] = self._compute_parsing_confidence(parsed)
        self.sudo().write(vals)

        # Compute and store match score (depends on job_id and job skills)
        self._compute_and_store_match_score()

    def _compute_parsing_confidence(self, parsed):
        """Compute confidence 0-100 from parsed data completeness."""
        score = 0.0
        if parsed.get('full_name'):
            score += 20.0
        if parsed.get('email'):
            score += 25.0
        if parsed.get('phone'):
            score += 15.0
        skills = parsed.get('skills') or []
        if skills:
            score += min(20.0, 20.0 * len(skills) / 5)
        if parsed.get('work_experience'):
            score += 20.0
        return round(min(100.0, score), 1)

    def _normalize_parsed_skills(self, parsed_skills):
        """Map parsed skill strings to hr.skill IDs using normalization table (and auto-create if enabled)."""
        if not parsed_skills:
            return []
        return self.env['resume.ai.parser.service'].sudo().normalize_skills(
            self.env, parsed_skills
        )

    def _compute_total_experience_years(self, parsed):
        """Compute total experience in years from parsed work_experience or total_experience_years."""
        service = self.env['resume.ai.parser.service'].sudo()
        return service.compute_experience_years(parsed)

    def _compute_and_store_match_score(self):
        """Calculate job match score and store in match_score."""
        for applicant in self:
            score = applicant._compute_match_score_value()
            applicant.sudo().match_score = score

    def _compute_match_score_value(self):
        """Algorithm: skill_score * 0.7 + experience_weight * 0.3."""
        self.ensure_one()
        job = self.job_id
        if not job:
            return 0.0
        required_skill_ids = getattr(job, 'skill_ids', self.env['hr.skill'])
        if not required_skill_ids:
            return 0.0
        matched = self.extracted_skill_ids & required_skill_ids
        skill_score = len(matched) / len(required_skill_ids)
        required_years = getattr(job, 'required_experience_years', None) or 0
        if required_years and required_years > 0:
            exp = self.total_experience_years or 0
            experience_weight = min(exp / required_years, 1.0)
        else:
            experience_weight = 1.0 if (self.total_experience_years or 0) > 0 else 0.0
        final = (skill_score * 0.7) + (experience_weight * 0.3)
        return round(final * 100, 2)

    @api.model
    def _cron_process_pending_resume_parsing(self):
        """Process applicants with parsing_status = 'pending' (when queue_job is not used)."""
        pending = self.search([('parsing_status', '=', 'pending')], limit=10)
        for applicant in pending:
            try:
                applicant._run_resume_parsing_single()
            except Exception as e:
                _logger.exception("Cron resume parsing failed for applicant %s: %s", applicant.id, e)
                applicant.sudo().write({
                    'parsing_status': 'error',
                    'parsing_error_message': str(e),
                })

    def action_reprocess_resume(self):
        """Set status to pending and trigger parsing again."""
        for applicant in self:
            applicant.write({
                'parsing_status': 'pending',
                'parsing_error_message': False,
            })
            applicant._trigger_resume_parsing()
        return True

    def _compute_resume_similarities(self):
        """Compute and store similarity pairs between this applicant and others with resume_text."""
        self.ensure_one()
        if not self.resume_text or len(self.resume_text) < 100:
            return
        Similarity = self.env['hr.resume.similarity'].sudo()
        Similarity.search([('applicant_id', '=', self.id)]).unlink()
        others = self.search([
            ('id', '!=', self.id),
            ('resume_text', '!=', False),
            ('resume_text', '!=', ''),
            ('parsing_status', '=', 'done'),
        ], limit=200)
        from .hr_resume_similarity import _jaccard_similarity
        pairs = []
        for other in others:
            score = _jaccard_similarity(self.resume_text, other.resume_text)
            if score >= 0.5:
                pairs.append((0, 0, {
                    'applicant_id': self.id,
                    'other_applicant_id': other.id,
                    'similarity_score': round(score, 4),
                }))
        if pairs:
            Similarity.create([p[2] for p in pairs])

    def action_compute_similarities(self):
        """Button: compute similarity for selected applicants."""
        self._compute_resume_similarities()
        return True

    def action_view_duplicates(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Possible duplicates'),
            'res_model': 'hr.applicant',
            'view_mode': 'list,form',
            'domain': [('id', 'in', self.duplicate_applicant_ids.ids)],
        }

    def action_view_similar_resumes(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Similar resumes'),
            'res_model': 'hr.resume.similarity',
            'view_mode': 'list,form',
            'domain': [('applicant_id', '=', self.id)],
            'context': {'default_applicant_id': self.id},
        }

    def action_view_parsed_data(self):
        """Open a dialog showing parsed JSON and extracted fields."""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Parsed Resume Data'),
            'res_model': 'hr.applicant',
            'res_id': self.id,
            'view_mode': 'form',
            'views': [(self.env.ref('hr_resume_ai_parser.hr_applicant_form_parsed_view').id, 'form')],
            'target': 'new',
        }
