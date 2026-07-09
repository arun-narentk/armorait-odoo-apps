# -*- coding: utf-8 -*-
"""Generate AI email drafts from business context."""

import logging

from odoo import models
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class RnAiEmailDraftService(models.AbstractModel):
    _name = 'rn.ai.email.draft.service'
    _description = 'AI Email Draft Service'

    def generate_draft(self, partner=None, template=None, res_model=None, res_id=None,
                       tone='professional', language='en', custom_prompt=None, preview_only=False):
        settings = self._get_settings()
        if not preview_only and settings.credit_balance <= 0:
            raise UserError('AI email credit balance is zero. Add credits to continue.')

        ctx = self.env['rn.ai.email.context.service'].build_context(
            partner=partner,
            res_model=res_model,
            res_id=res_id,
        )
        category = template.category if template else 'general'
        subject, body = self._build_content(ctx, category, tone, template, custom_prompt)
        body = self.env['rn.ai.email.tone.service'].apply_tone(body, tone)
        if language != 'en':
            body = self.env['rn.ai.email.translation.service'].translate_stub(body, language)

        if not preview_only:
            settings.credit_balance -= 1
        return {
            'subject': subject,
            'body_html': f'<p>{body}</p>',
            'context_summary': self.env['rn.ai.email.context.service'].context_to_text(ctx),
        }

    def _build_content(self, ctx, category, tone, template, custom_prompt):
        partner = ctx.get('partner_name') or 'Customer'
        company = ctx.get('company_name') or 'Our team'

        if category == 'sales' or ctx.get('quotation'):
            subject = f'Follow-up on quotation {ctx.get("quotation", "")}'
            body = (
                f'Dear {partner},\n\n'
                f'I hope you are doing well. I wanted to follow up on quotation '
                f'{ctx.get("quotation", "")} for {ctx.get("products", "your requested items")} '
                f'({ctx.get("amount_total", "")} {ctx.get("currency", "")}).\n\n'
                f'Please let us know if you have any questions. We would be happy to help.\n\n'
                f'Best regards,\n{ctx.get("salesperson", company)}'
            )
        elif category == 'accounting' or ctx.get('invoice'):
            overdue = ctx.get('overdue_days', 0)
            if overdue and overdue > 30:
                subject = f'Payment reminder: invoice {ctx.get("invoice", "")}'
                body = (
                    f'Dear {partner},\n\n'
                    f'This is a reminder that invoice {ctx.get("invoice", "")} '
                    f'for {ctx.get("amount_due", "")} is overdue by {overdue} days. '
                    f'Please arrange payment at your earliest convenience.\n\n'
                    f'Regards,\n{company}'
                )
            else:
                subject = f'Friendly reminder: invoice {ctx.get("invoice", "")}'
                body = (
                    f'Dear {partner},\n\n'
                    f'We noticed invoice {ctx.get("invoice", "")} with balance '
                    f'{ctx.get("amount_due", "")} is pending. '
                    f'Due date: {ctx.get("due_date", "N/A")}.\n\n'
                    f'Thank you,\n{company}'
                )
        elif category == 'crm' or ctx.get('lead'):
            subject = f'Following up on {ctx.get("lead", "your inquiry")}'
            body = (
                f'Dear {partner},\n\n'
                f'Thank you for your interest. I wanted to follow up on '
                f'{ctx.get("lead", "your request")}. '
                f'We would be glad to schedule a short call to discuss next steps.\n\n'
                f'Best regards,\n{ctx.get("salesperson", company)}'
            )
        else:
            subject = template.subject_pattern if template and template.subject_pattern else 'Message from ' + company
            body = custom_prompt or (
                f'Dear {partner},\n\n'
                f'Thank you for your continued partnership with {company}.\n\n'
                f'Best regards,\n{ctx.get("salesperson", company)}'
            )
        return subject.strip(), body.strip()

    def _get_settings(self):
        settings = self.env['rn.ai.email.settings'].search(
            [('company_id', '=', self.env.company.id)], limit=1,
        )
        if not settings:
            settings = self.env['rn.ai.email.settings'].create({
                'company_id': self.env.company.id,
            })
        return settings
