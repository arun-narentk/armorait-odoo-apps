# -*- coding: utf-8 -*-

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    ai_email_default_tone = fields.Selection(
        related='company_id.ai_email_default_tone',
        readonly=False,
    )
    ai_email_default_language = fields.Selection(
        related='company_id.ai_email_default_language',
        readonly=False,
    )


class ResCompany(models.Model):
    _inherit = 'res.company'

    ai_email_default_tone = fields.Selection(
        selection=[
            ('professional', 'Professional'),
            ('friendly', 'Friendly'),
            ('formal', 'Formal'),
        ],
        default='professional',
    )
    ai_email_default_language = fields.Selection(
        selection=[('en', 'English'), ('ta', 'Tamil'), ('hi', 'Hindi')],
        default='en',
    )
