# -*- coding: utf-8 -*-

from odoo import http
from odoo.http import request


class RnSmartColorTagsController(http.Controller):

    @http.route("/rn_visual_enhancer/tags", type="json", auth="user")
    def get_color_tags(self, model, record_ids):
        if not model or not record_ids:
            return {}
        service = request.env["rn.color.rule.service"]
        return service.get_tags_for_web(model, record_ids)
