# -*- coding: utf-8 -*-
"""Send document for signature wizard."""

from datetime import timedelta

from odoo import fields, models
from odoo.exceptions import UserError


class RnDocSendSignatureWizard(models.TransientModel):
    _name = 'rn.doc.send.signature.wizard'
    _description = 'Send for Signature'

    res_model = fields.Char()
    res_id = fields.Integer()
    document_name = fields.Char()
    attachment_id = fields.Many2one('ir.attachment', string='PDF Document', required=True)
    template_id = fields.Many2one('rn.doc.platform.template')
    sign_mode = fields.Selection(
        selection=[('sequential', 'Sequential'), ('parallel', 'Parallel')],
        default='sequential',
    )
    signer_name = fields.Char(string='Signer Name', required=True)
    signer_email = fields.Char(string='Signer Email', required=True)
    signer_partner_id = fields.Many2one('res.partner')
    note = fields.Html()

    def action_send(self):
        self.ensure_one()
        if not self.attachment_id:
            raise UserError('Attach a PDF document to send for signature.')

        settings = self.env['rn.doc.platform.settings'].search(
            [('company_id', '=', self.env.company.id)], limit=1,
        )
        expiry_days = settings.default_expiry_days if settings else 14
        expiry = fields.Date.context_today(self) + timedelta(days=expiry_days)

        request = self.env['rn.doc.sign.request'].create({
            'template_id': self.template_id.id if self.template_id else False,
            'attachment_id': self.attachment_id.id,
            'res_model': self.res_model,
            'res_id': self.res_id,
            'sign_mode': self.sign_mode,
            'expiry_date': expiry,
            'note': self.note,
            'company_id': self.env.company.id,
        })
        self.env['rn.doc.sign.signer'].create({
            'request_id': request.id,
            'name': self.signer_name,
            'email': self.signer_email,
            'partner_id': self.signer_partner_id.id if self.signer_partner_id else False,
            'sequence': 10,
        })

        if self.res_model and self.res_id:
            doc = self.env[self.res_model].browse(self.res_id)
            if doc.exists() and hasattr(doc, 'sign_request_id'):
                doc.sign_request_id = request.id

        self.env['rn.doc.sign.service'].send_request(request)
        return {
            'type': 'ir.actions.act_window',
            'name': 'Sign Request',
            'res_model': 'rn.doc.sign.request',
            'view_mode': 'form',
            'res_id': request.id,
        }
