# -*- coding: utf-8 -*-

from odoo import http
from odoo.http import request


class AiBizPromotionController(http.Controller):
    """Public website route for the AI BIZ promotional landing page."""

    @http.route(
        '/ai-biz',
        type='http',
        auth='public',
        website=True,
        sitemap=True,
    )
    def ai_biz_landing(self, **kwargs):
        promotion = request.env['ai.biz.promotion.service'].sudo().get_active_promotion()
        return request.render(
            'rn_ai_biz_promotion.ai_biz_landing_page',
            {
                'promotion': promotion,
                'benefits': promotion.benefit_ids if promotion else request.env['ai.biz.benefit'],
            },
        )
