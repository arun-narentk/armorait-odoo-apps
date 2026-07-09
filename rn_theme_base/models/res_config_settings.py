from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    tb_primary_color = fields.Char(
        related='website_id.tb_primary_color',
        readonly=False,
    )
    tb_secondary_color = fields.Char(
        related='website_id.tb_secondary_color',
        readonly=False,
    )
    tb_accent_color = fields.Char(
        related='website_id.tb_accent_color',
        readonly=False,
    )
    tb_heading_font = fields.Char(
        related='website_id.tb_heading_font',
        readonly=False,
    )
    tb_body_font = fields.Char(
        related='website_id.tb_body_font',
        readonly=False,
    )
    tb_enable_animations = fields.Boolean(
        related='website_id.tb_enable_animations',
        readonly=False,
    )
    tb_sticky_header = fields.Boolean(
        related='website_id.tb_sticky_header',
        readonly=False,
    )
    tb_whatsapp_number = fields.Char(
        related='website_id.tb_whatsapp_number',
        readonly=False,
    )
    tb_show_emergency_banner = fields.Boolean(
        related='website_id.tb_show_emergency_banner',
        readonly=False,
    )
    tb_emergency_banner_text = fields.Char(
        related='website_id.tb_emergency_banner_text',
        readonly=False,
    )
