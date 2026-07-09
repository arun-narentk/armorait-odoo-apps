# -*- coding: utf-8 -*-
"""Individual signer on a sign request."""

from odoo import fields, models
from odoo.exceptions import UserError

SIGNER_STATES = [
    ('pending', 'Pending'),
    ('sent', 'Invitation Sent'),
    ('signed', 'Signed'),
    ('declined', 'Declined'),
]


class RnDocSignSigner(models.Model):
    """Signer invited to sign a document."""

    _name = 'rn.doc.sign.signer'
    _description = 'Document Signer'
    _order = 'sequence, id'

    request_id = fields.Many2one(
        'rn.doc.sign.request',
        required=True,
        ondelete='cascade',
        index=True,
    )
    sequence = fields.Integer(default=10)
    partner_id = fields.Many2one('res.partner', string='Signer Contact')
    email = fields.Char(required=True)
    name = fields.Char(required=True)
    role = fields.Selection(
        selection=[
            ('signer', 'Signer'),
            ('approver', 'Approver'),
            ('witness', 'Witness'),
            ('customer', 'Customer'),
            ('vendor', 'Vendor'),
        ],
        default='signer',
    )
    state = fields.Selection(selection=SIGNER_STATES, default='pending', index=True)
    sign_method = fields.Selection(
        selection=[
            ('email_otp', 'Email OTP'),
            ('draw', 'Draw Signature'),
            ('upload', 'Upload Signature'),
            ('aadhaar', 'Aadhaar eSign'),
            ('dsc', 'DSC Token'),
        ],
        default='draw',
    )
    signed_on = fields.Datetime()
    signature_image = fields.Binary(string='Signature Image')
    access_token = fields.Char(index=True)
    is_active = fields.Boolean(default=False, string='Current Signer')
    company_id = fields.Many2one(related='request_id.company_id', store=True)

    def action_mark_signed(self):
        for signer in self:
            self.env['rn.doc.sign.service'].complete_signer(signer)
        return True

    def action_decline(self):
        for signer in self:
            if signer.state not in ('pending', 'sent'):
                raise UserError('Signer already responded.')
            signer.write({'state': 'declined'})
            signer.request_id.write({'state': 'declined'})
        return True
