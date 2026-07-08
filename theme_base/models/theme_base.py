from odoo import models


class ThemeUtils(models.AbstractModel):
    _inherit = 'theme.utils'

    @property
    def _header_templates(self):
        return [
            'theme_base.template_header_tb_sticky',
            'theme_base.template_header_tb_search',
        ] + super()._header_templates

    @property
    def _footer_templates(self):
        return [
            'theme_base.template_footer_tb_minimal',
            'theme_base.template_footer_tb_columns',
        ] + super()._footer_templates

    def _theme_base_post_copy(self, mod):
        self.enable_view('theme_base.template_header_tb_sticky')
        self.enable_view('theme_base.template_footer_tb_columns')
        self.enable_view('theme_base.tb_breadcrumb')
        self.enable_view('theme_base.tb_search_modal')
        self.enable_asset('website.ripple_effect_scss')
        self.enable_asset('website.ripple_effect_js')
