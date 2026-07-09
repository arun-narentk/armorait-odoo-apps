# -*- coding: utf-8 -*-
"""Partner extensions for messaging contacts."""

from odoo import fields, models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    rn_messaging_external_ids = fields.Char(
        string='Messaging External IDs',
        help='Comma-separated channel identifiers linked to this contact.',
    )
