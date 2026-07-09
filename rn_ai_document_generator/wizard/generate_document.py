# -*- coding: utf-8 -*-
"""Wizard to compose and generate an AI document."""

from odoo import api, fields, models


class RnAiDocumentGenerateWizard(models.TransientModel):
    _name = 'rn.ai.document.generate.wizard'
    _description = 'Generate AI Document'

    type_id = fields.Many2one('rn.ai.document.type', required=True)
    template_id = fields.Many2one('rn.ai.document.template', required=True)
    partner_id = fields.Many2one('res.partner', string='Customer / Vendor')
    employee_id = fields.Many2one('hr.employee', string='Employee')
    language = fields.Selection(
        selection=[
            ('en', 'English'),
            ('ta', 'Tamil'),
            ('hi', 'Hindi'),
            ('ar', 'Arabic'),
            ('fr', 'French'),
            ('de', 'German'),
        ],
        default='en',
        required=True,
    )
    style = fields.Selection(
        selection=[
            ('formal', 'Formal'),
            ('corporate', 'Corporate'),
            ('legal', 'Legal'),
            ('friendly', 'Friendly'),
            ('executive', 'Executive'),
            ('technical', 'Technical'),
            ('marketing', 'Marketing'),
        ],
        default='formal',
        required=True,
    )
    subject = fields.Char()
    res_model = fields.Char()
    res_id = fields.Integer()
    generate_now = fields.Boolean(default=True)

    @api.onchange('type_id')
    def _onchange_type_id(self):
        if self.type_id:
            self.style = self.type_id.default_style or self.style
            return {'domain': {'template_id': [('type_id', '=', self.type_id.id)]}}
        return {'domain': {'template_id': []}}

    @api.onchange('template_id')
    def _onchange_template_id(self):
        if self.template_id:
            self.language = self.template_id.language
            self.style = self.template_id.style

    def action_generate(self):
        self.ensure_one()
        document = self.env['rn.ai.document'].create({
            'type_id': self.type_id.id,
            'template_id': self.template_id.id,
            'partner_id': self.partner_id.id,
            'employee_id': self.employee_id.id,
            'language': self.language,
            'style': self.style,
            'subject': self.subject or self.template_id.name,
            'res_model': self.res_model,
            'res_id': self.res_id,
        })
        if self.generate_now:
            self.env['rn.ai.document.render.service'].generate_documents(document)
        return {
            'type': 'ir.actions.act_window',
            'name': 'Document',
            'res_model': 'rn.ai.document',
            'res_id': document.id,
            'view_mode': 'form',
            'target': 'current',
        }
