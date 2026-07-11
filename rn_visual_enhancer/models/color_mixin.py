# -*- coding: utf-8 -*-

from odoo import api, fields, models

from ..constants import COLOR_SELECTION, ICON_SELECTION


class RnColorMixin(models.AbstractModel):
    _name = "rn.color.mixin"
    _description = "Color Tag Mixin"

    rn_color_tag_rule_id = fields.Many2one("rn.color.rule", readonly=True, index=True)
    rn_color_tag_color = fields.Selection(selection=COLOR_SELECTION, readonly=True, index=True)
    rn_color_tag_icon = fields.Selection(selection=ICON_SELECTION, readonly=True)
    rn_color_tag_label = fields.Char(readonly=True, index=True)
    rn_color_tag_emoji = fields.Char(readonly=True)
    rn_color_tag_css_class = fields.Char(readonly=True)

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        if not self.env.context.get("rn_skip_color_refresh"):
            records._rn_refresh_color_tags()
        return records

    def write(self, vals):
        result = super().write(vals)
        if self.env.context.get("rn_skip_color_refresh"):
            return result
        if any(field_name.startswith("rn_color_tag_") for field_name in vals):
            return result
        self._rn_refresh_color_tags()
        return result

    def _rn_refresh_color_tags(self):
        if not self:
            return
        service = self.env["rn.color.rule.service"]
        tag_map = service.get_tags_batch(self._name, self.ids)
        for record in self:
            tag = tag_map.get(record.id) or {}
            values = {
                "rn_color_tag_rule_id": tag.get("rule_id") or False,
                "rn_color_tag_color": tag.get("color") or False,
                "rn_color_tag_icon": tag.get("icon") or "none",
                "rn_color_tag_label": tag.get("label") or False,
                "rn_color_tag_emoji": tag.get("emoji") or False,
                "rn_color_tag_css_class": tag.get("css_class") or False,
            }
            record.with_context(rn_skip_color_refresh=True).write(values)
