# -*- coding: utf-8 -*-

from odoo import _, api, fields, models


class MarginOverrideWizard(models.TransientModel):
    _name = 'margin.override.wizard'
    _description = 'Margin Override Approval'

    order_id = fields.Many2one('sale.order', string='Sale Order', required=True, ondelete='cascade')
    reason = fields.Text(string='Reason', required=True)
    approved_by_id = fields.Many2one(
        'res.users',
        string='Approved By',
        default=lambda self: self.env.user,
        required=True,
    )

    def action_confirm_override(self):
        self.ensure_one()
        order = self.order_id
        if order.state not in ('draft', 'sent'):
            return {'type': 'ir.actions.act_window_close'}
        for line in order.order_line.filtered(lambda l: not l.display_type and l.margin_status == 'danger'):
            self.env['margin.violation.log'].create({
                'order_id': order.id,
                'order_line_id': line.id,
                'margin_pct': line.real_margin,
                'status': 'override',
                'reason': self.reason,
                'approved_by_id': self.approved_by_id.id,
            })
        body = _('Margin override: %s\nApproved by: %s') % (self.reason, self.approved_by_id.name)
        order.message_post(body=body, message_type='notification', subtype_xmlid='mail.mt_note')
        order.margin_blocked = False
        order.with_context(margin_override=True).action_confirm()
        return {'type': 'ir.actions.act_window_close'}
