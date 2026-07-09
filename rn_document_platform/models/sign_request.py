# -*- coding: utf-8 -*-
"""Sign request for a business document."""

import secrets

from odoo import api, fields, models
from odoo.exceptions import UserError

REQUEST_STATES = [
    ('draft', 'Draft'),
    ('sent', 'Sent for Signature'),
    ('partial', 'Partially Signed'),
    ('completed', 'Completed'),
    ('declined', 'Declined'),
    ('expired', 'Expired'),
    ('cancelled', 'Cancelled'),
]


class RnDocSignRequest(models.Model):
    """Document signing request with multi-signer workflow."""

    _name = 'rn.doc.sign.request'
    _description = 'Document Sign Request'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'create_date desc'

    name = fields.Char(required=True, default='New', tracking=True)
    reference = fields.Char(copy=False, index=True, default='New')
    state = fields.Selection(selection=REQUEST_STATES, default='draft', tracking=True, index=True)
    template_id = fields.Many2one('rn.doc.platform.template')
    attachment_id = fields.Many2one('ir.attachment', string='PDF Document', required=True)
    res_model = fields.Char(index=True)
    res_id = fields.Integer(index=True)
    document_display = fields.Char(compute='_compute_document_display', store=True)
    sign_mode = fields.Selection(
        selection=[
            ('sequential', 'Sequential'),
            ('parallel', 'Parallel'),
        ],
        default='sequential',
        required=True,
    )
    signer_ids = fields.One2many('rn.doc.sign.signer', 'request_id', string='Signers')
    field_ids = fields.One2many('rn.doc.sign.field', 'request_id', string='Signature Fields')
    audit_ids = fields.One2many('rn.doc.sign.audit', 'request_id', string='Audit Trail')
    analysis_id = fields.Many2one('rn.doc.ai.analysis', string='AI Analysis')
    expiry_date = fields.Date()
    access_token = fields.Char(copy=False, index=True)
    signed_attachment_id = fields.Many2one('ir.attachment', string='Signed PDF', copy=False)
    document_hash = fields.Char(string='Document SHA256', copy=False)
    requester_id = fields.Many2one(
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
    note = fields.Html()

    @api.depends('res_model', 'res_id')
    def _compute_document_display(self):
        for req in self:
            label = req.name
            if req.res_model and req.res_id:
                try:
                    doc = self.env[req.res_model].browse(req.res_id)
                    if doc.exists():
                        label = doc.display_name
                except Exception:
                    pass
            req.document_display = label

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('reference', 'New') == 'New':
                vals['reference'] = (
                    self.env['ir.sequence'].next_by_code('rn.doc.sign.request') or 'New'
                )
            if vals.get('name', 'New') == 'New':
                vals['name'] = vals.get('reference', 'New')
            if not vals.get('access_token'):
                vals['access_token'] = secrets.token_urlsafe(32)
        records = super().create(vals_list)
        for rec in records:
            if rec.attachment_id and not rec.attachment_id.res_id:
                rec.attachment_id.write({'res_model': rec._name, 'res_id': rec.id})
        return records

    def action_send(self):
        for req in self:
            if not req.signer_ids:
                raise UserError('Add at least one signer before sending.')
            self.env['rn.doc.sign.service'].send_request(req)
        return True

    def action_cancel(self):
        self.write({'state': 'cancelled'})

    def action_open_document(self):
        self.ensure_one()
        if not self.res_model or not self.res_id:
            return False
        return {
            'type': 'ir.actions.act_window',
            'res_model': self.res_model,
            'view_mode': 'form',
            'res_id': self.res_id,
        }

    def action_run_ai_analysis(self):
        for req in self:
            analysis = self.env['rn.doc.ai.analysis.service'].analyze_request(req)
            req.analysis_id = analysis.id
        return True
