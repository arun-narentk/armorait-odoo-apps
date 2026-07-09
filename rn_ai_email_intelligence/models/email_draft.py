# -*- coding: utf-8 -*-
"""AI-generated email draft with review workflow."""

from odoo import api, fields, models
from odoo.exceptions import UserError

DRAFT_STATES = [
    ('draft', 'Draft'),
    ('review', 'Ready to Review'),
    ('sent', 'Sent'),
    ('discarded', 'Discarded'),
]


class RnAiEmailDraft(models.Model):
    _name = 'rn.ai.email.draft'
    _description = 'AI Email Draft'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'create_date desc'

    name = fields.Char(required=True, default='New')
    reference = fields.Char(copy=False, index=True, default='New')
    state = fields.Selection(selection=DRAFT_STATES, default='draft', tracking=True, index=True)
    template_id = fields.Many2one('rn.ai.email.template')
    category = fields.Selection(related='template_id.category', store=True)
    partner_id = fields.Many2one('res.partner', index=True)
    partner_email = fields.Char()
    subject = fields.Char(required=True)
    body_html = fields.Html(required=True)
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
            ('en', 'English'),
            ('ta', 'Tamil'),
            ('hi', 'Hindi'),
            ('fr', 'French'),
            ('de', 'German'),
            ('ar', 'Arabic'),
            ('es', 'Spanish'),
        ],
        default='en',
    )
    res_model = fields.Char(index=True)
    res_id = fields.Integer(index=True)
    context_summary = fields.Text(string='AI Context Used', copy=False)
    mail_message_id = fields.Many2one('mail.message', copy=False)
    user_id = fields.Many2one(
        'res.users',
        default=lambda self: self.env.user,
        required=True,
    )
    company_id = fields.Many2one(
        'res.company',
        required=True,
        default=lambda self: self.env.company,
        index=True,
    )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('reference', 'New') == 'New':
                vals['reference'] = (
                    self.env['ir.sequence'].next_by_code('rn.ai.email.draft') or 'New'
                )
            if vals.get('name', 'New') == 'New':
                vals['name'] = vals.get('reference', 'New')
        return super().create(vals_list)

    def action_regenerate(self):
        for draft in self:
            result = self.env['rn.ai.email.draft.service'].generate_draft(
                partner=draft.partner_id,
                template=draft.template_id,
                res_model=draft.res_model,
                res_id=draft.res_id,
                tone=draft.tone,
                language=draft.language,
            )
            draft.write({
                'subject': result['subject'],
                'body_html': result['body_html'],
                'context_summary': result['context_summary'],
                'state': 'review',
            })
        return True

    def action_send_email(self):
        self.ensure_one()
        if not self.partner_email and not self.partner_id.email:
            raise UserError('Recipient email is required.')
        email_to = self.partner_email or self.partner_id.email
        mail = self.env['mail.mail'].create({
            'subject': self.subject,
            'body_html': self.body_html,
            'email_to': email_to,
            'author_id': self.env.user.partner_id.id,
        })
        mail.send()
        self.write({'state': 'sent'})
        if self.res_model and self.res_id:
            doc = self.env[self.res_model].browse(self.res_id)
            if doc.exists() and hasattr(doc, 'message_post'):
                doc.message_post(
                    body=f'AI email sent: {self.subject}',
                    subject=self.subject,
                )
        return True

    def action_discard(self):
        self.write({'state': 'discarded'})
