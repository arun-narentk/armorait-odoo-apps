# -*- coding: utf-8 -*-
"""Settings for quotation expiry countdown warning threshold."""

from odoo import fields, models

from .sale_order import DEFAULT_WARNING_HOURS, PARAM_WARNING_HOURS


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    rn_quotation_expiry_warning_hours = fields.Integer(
        string='Quotation Expiry Warning (Hours)',
        config_parameter=PARAM_WARNING_HOURS,
        default=DEFAULT_WARNING_HOURS,
        help=(
            'Show an orange warning countdown when less than this many hours '
            'remain before the quotation expiration date (end of day).'
        ),
    )
