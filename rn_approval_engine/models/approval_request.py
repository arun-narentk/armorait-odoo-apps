# -*- coding: utf-8 -*-
"""Runtime approval request linked to any document."""

from odoo import api, fields, models
from odoo.exceptions import UserError

REQUEST_STATES = [
    ('draft', 'Draft'),
    ('pending', 'Pending Approval'),
    ('approved', 'Approved'),
    ('rejected', 'Rejected'),
    ('cancelled', 'Cancelled'),
]


class RnApprovalRequest(models.Model):
    """Approval instance for a business document."""

    _name = 'rn.approval.request'
    _description = 'Approval Request'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'create_date desc'

    name = fields.Char(required=True, default='New', tracking=True)
    reference = fields.Char(copy=False, index=True, default='New')
    state = fields.Selection(selection=REQUEST_STATES, default='draft', tracking=True, index=True)
    workflow_id = fields.Many2one('rn.approval.workflow', required=True, tracking=True)
    res_model = fields.Char(required=True, index=True)
    res_id = fields.Integer(required=True, index=True)
    document_display = fields.Char(compute='_compute_document_display', store=True)
    amount = fields.Monetary(currency_field='currency_id')
    currency_id = fields.Many2one(
        'res.currency',
        default=lambda self: self.env.company.currency_id,
    )
    requester_id = fields.Many2one(
        'res.users',
        default=lambda self: self.env.user,
        required=True,
        tracking=True,
    )
    current_stage_id = fields.Many2one('rn.approval.workflow.stage', string='Current Stage')
    line_ids = fields.One2many('rn.approval.request.line', 'request_id', string='Approvers')
    history_ids = fields.One2many('rn.approval.history', 'request_id', string='History')
    pending_line_count = fields.Integer(compute='_compute_line_counts')
    approved_line_count = fields.Integer(compute='_compute_line_counts')
    risk_summary = fields.Html(string='AI Risk Summary', copy=False)
    sla_deadline = fields.Datetime(string='SLA Deadline')
    is_overdue = fields.Boolean(compute='_compute_is_overdue')
    company_id = fields.Many2one(
        'res.company',
        required=True,
        default=lambda self: self.env.company,
        index=True,
    )

    @api.depends('res_model', 'res_id')
    def _compute_document_display(self):
        for req in self:
            label = f'{req.res_model},{req.res_id}'
            if req.res_model and req.res_id:
                try:
                    doc = self.env[req.res_model].browse(req.res_id)
                    if doc.exists():
                        label = doc.display_name
                except Exception:
                    pass
            req.document_display = label

    @api.depends('line_ids.state')
    def _compute_line_counts(self):
        for req in self:
            req.pending_line_count = len(req.line_ids.filtered(lambda l: l.state == 'pending'))
            req.approved_line_count = len(req.line_ids.filtered(lambda l: l.state == 'approved'))

    @api.depends('sla_deadline', 'state')
    def _compute_is_overdue(self):
        now = fields.Datetime.now()
        for req in self:
            req.is_overdue = bool(
                req.state == 'pending' and req.sla_deadline and req.sla_deadline < now
            )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('reference', 'New') == 'New':
                vals['reference'] = (
                    self.env['ir.sequence'].next_by_code('rn.approval.request') or 'New'
                )
            if vals.get('name', 'New') == 'New':
                vals['name'] = vals.get('reference', 'New')
        return super().create(vals_list)

    def action_submit(self):
        for req in self:
            if req.state != 'draft':
                raise UserError('Only draft requests can be submitted.')
            self.env['rn.approval.engine.service'].submit_request(req)
        return True

    def action_cancel(self):
        self.write({'state': 'cancelled'})

    def action_open_document(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'res_model': self.res_model,
            'view_mode': 'form',
            'res_id': self.res_id,
        }
