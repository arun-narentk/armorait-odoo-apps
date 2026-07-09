# -*- coding: utf-8 -*-
"""Compose AI email wizard."""

from odoo import api, fields, models


class RnAiEmailComposeWizard(models.TransientModel):
    _name = 'rn.ai.email.compose.wizard'
    _description = 'Compose AI Email'

    partner_id = fields.Many2one('res.partner')
    template_id = fields.Many2one('rn.ai.email.template')
    res_model = fields.Char()
    res_id = fields.Integer()
    tone = fields.Selection(
        selection=[
            ('professional', 'Professional'),
            ('friendly', 'Friendly'),
            ('executive', 'Executive'),
            ('formal', 'Formal'),
            ('persuasive', 'Persuasive'),
            ('apologetic', 'Apologetic'),
            ('concise', 'Concise'),
            ('followup', 'Follow-up Focused'),
        ],
        default='professional',
    )
    language = fields.Selection(
        selection=[
            ('en', 'English'), ('ta', 'Tamil'), ('hi', 'Hindi'),
            ('fr', 'French'), ('de', 'German'), ('ar', 'Arabic'), ('es', 'Spanish'),
        ],
        default='en',
    )
    custom_prompt = fields.Text(string='Extra Instructions')
    subject = fields.Char()
    body_html = fields.Html()

    @api.onchange('template_id', 'partner_id', 'res_model', 'res_id', 'tone', 'language')
    def _onchange_generate_preview(self):
        if not self.partner_id and not self.res_model:
            return
        try:
            result = self.env['rn.ai.email.draft.service'].generate_draft(
                partner=self.partner_id,
                template=self.template_id,
                res_model=self.res_model,
                res_id=self.res_id or 0,
                tone=self.tone,
                language=self.language,
                custom_prompt=self.custom_prompt,
                preview_only=True,
            )
            self.subject = result['subject']
            self.body_html = result['body_html']
        except Exception:
            pass

    def action_save_draft(self):
        self.ensure_one()
        draft = self.env['rn.ai.email.draft'].create({
            'template_id': self.template_id.id if self.template_id else False,
            'partner_id': self.partner_id.id if self.partner_id else False,
            'partner_email': self.partner_id.email if self.partner_id else False,
            'subject': self.subject,
            'body_html': self.body_html,
            'tone': self.tone,
            'language': self.language,
            'res_model': self.res_model,
            'res_id': self.res_id,
            'state': 'review',
            'company_id': self.env.company.id,
        })
        if not self.subject or not self.body_html:
            result = self.env['rn.ai.email.draft.service'].generate_draft(
                partner=self.partner_id,
                template=self.template_id,
                res_model=self.res_model,
                res_id=self.res_id or 0,
                tone=self.tone,
                language=self.language,
                custom_prompt=self.custom_prompt,
            )
            draft.write({
                'subject': result['subject'],
                'body_html': result['body_html'],
                'context_summary': result['context_summary'],
            })
        return {
            'type': 'ir.actions.act_window',
            'name': 'Email Draft',
            'res_model': 'rn.ai.email.draft',
            'view_mode': 'form',
            'res_id': draft.id,
        }

    def action_send_now(self):
        self.ensure_one()
        action = self.action_save_draft()
        draft = self.env['rn.ai.email.draft'].browse(action['res_id'])
        draft.action_send_email()
        return {'type': 'ir.actions.act_window_close'}
