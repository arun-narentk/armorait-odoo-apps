# -*- coding: utf-8 -*-
"""Generated AI document record."""

from odoo import api, fields, models


class RnAiDocument(models.Model):
    """Working document with preview, AI body, and lifecycle state."""

    _name = 'rn.ai.document'
    _description = 'AI Document'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'create_date desc, id desc'

    name = fields.Char(required=True, copy=False, default='New', tracking=True)
    type_id = fields.Many2one('rn.ai.document.type', required=True, tracking=True, index=True)
    template_id = fields.Many2one('rn.ai.document.template', required=True, tracking=True)
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
    state = fields.Selection(
        selection=[
            ('draft', 'Draft'),
            ('generated', 'Generated'),
            ('to_approve', 'Pending Approval'),
            ('approved', 'Approved'),
            ('rejected', 'Rejected'),
            ('final', 'Final'),
            ('sent', 'Sent'),
            ('signed', 'Signed'),
            ('cancelled', 'Cancelled'),
        ],
        default='draft',
        tracking=True,
        index=True,
    )
    partner_id = fields.Many2one('res.partner', string='Customer / Vendor')
    employee_id = fields.Many2one('hr.employee', string='Employee')
    user_id = fields.Many2one('res.users', string='Owner', default=lambda self: self.env.user)
    res_model = fields.Char(string='Source Model', index=True)
    res_id = fields.Integer(string='Source Record', index=True)
    subject = fields.Char()
    body_html = fields.Html(string='Document Body', sanitize=False)
    ai_notes = fields.Text(string='AI Generation Notes')
    placeholder_values = fields.Text(string='Resolved Placeholders (JSON)')
    version_count = fields.Integer(compute='_compute_version_count')
    version_ids = fields.One2many('rn.ai.document.version', 'document_id', string='Versions')
    approval_ids = fields.One2many('rn.ai.document.approval', 'document_id', string='Approvals')
    company_id = fields.Many2one(
        'res.company',
        required=True,
        default=lambda self: self.env.company,
        index=True,
    )
    signed_date = fields.Datetime()
    sent_date = fields.Datetime()
    note = fields.Html()

    @api.depends('version_ids')
    def _compute_version_count(self):
        for doc in self:
            doc.version_count = len(doc.version_ids)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', 'New') == 'New':
                vals['name'] = self.env['ir.sequence'].next_by_code('rn.ai.document') or 'New'
        return super().create(vals_list)

    def action_generate(self):
        return self.env['rn.ai.document.render.service'].generate_documents(self)

    def action_submit_approval(self):
        return self.env['rn.ai.document.approval.service'].submit(self)

    def action_approve(self):
        return self.env['rn.ai.document.approval.service'].approve(self)

    def action_reject(self):
        return self.env['rn.ai.document.approval.service'].reject(self)

    def action_mark_final(self):
        self.write({'state': 'final'})
        self.env['rn.ai.document.version.service'].snapshot(self, reason='Marked final')
        return True

    def action_mark_sent(self):
        self.write({'state': 'sent', 'sent_date': fields.Datetime.now()})
        return True

    def action_mark_signed(self):
        return self.env['rn.ai.document.signature.service'].mark_signed(self)

    def action_print_pdf(self):
        self.ensure_one()
        return self.env.ref('rn_ai_document_generator.action_report_rn_ai_document').report_action(self)

    def action_open_versions(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Versions',
            'res_model': 'rn.ai.document.version',
            'view_mode': 'list,form',
            'domain': [('document_id', '=', self.id)],
            'context': {'default_document_id': self.id},
        }
