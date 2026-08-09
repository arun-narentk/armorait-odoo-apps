# -*- coding: utf-8 -*-

import logging

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError
from odoo.tools.safe_eval import safe_eval

from ..constants import COLOR_SELECTION, ICON_SELECTION

_logger = logging.getLogger(__name__)


class RnColorRule(models.Model):
    _name = "rn.color.rule"
    _description = "Smart Color Rule"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "priority desc, id asc"

    name = fields.Char(required=True, tracking=True)
    active = fields.Boolean(default=True, tracking=True)
    model_id = fields.Many2one(
        "ir.model",
        required=True,
        ondelete="cascade",
        index=True,
        domain=[("transient", "=", False)],
        tracking=True,
    )
    model_name = fields.Char(related="model_id.model", store=True, index=True)
    domain = fields.Text(required=True, default="[]", tracking=True)
    color = fields.Selection(
        selection=COLOR_SELECTION,
        required=True,
        default="gray",
        index=True,
        tracking=True,
    )
    icon = fields.Selection(selection=ICON_SELECTION, default="none", tracking=True)
    emoji = fields.Char(tracking=True)
    label = fields.Char(required=True, tracking=True)
    priority = fields.Integer(default=50, index=True, tracking=True)
    company_id = fields.Many2one(
        "res.company",
        required=True,
        default=lambda self: self.env.company,
        index=True,
        tracking=True,
    )

    _sql_constraints = [
        (
            "rn_color_rule_priority_check",
            "CHECK(priority >= 0)",
            "Priority must be zero or higher.",
        ),
    ]

    @api.constrains("domain")
    def _check_domain_expression(self):
        for rule in self:
            try:
                parsed = safe_eval(rule.domain or "[]", {"context_today": fields.Date.context_today})
            except Exception as exc:
                raise ValidationError(_("Invalid domain expression: %s") % exc) from exc
            if not isinstance(parsed, (list, tuple)):
                raise ValidationError(_("Domain expression must evaluate to a list or tuple."))

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        if not self.env.context.get("install_mode"):
            records._rn_recompute_impacted_models()
        return records

    def write(self, vals):
        impacted_before = {(rule.model_name, rule.company_id.id) for rule in self}
        result = super().write(vals)
        if self.env.context.get("rn_skip_color_recompute"):
            self.env["rn.color.rule.service"].clear_rule_cache()
            return result
        impacted_after = {(rule.model_name, rule.company_id.id) for rule in self}
        self.env["rn.color.rule.service"].clear_rule_cache()
        for model_name, company_id in impacted_before | impacted_after:
            self.env["rn.color.rule.service"].recompute_model_tags(model_name, company_id=company_id)
        return result

    def unlink(self):
        impacted = {(rule.model_name, rule.company_id.id) for rule in self}
        result = super().unlink()
        self.env["rn.color.rule.service"].clear_rule_cache()
        for model_name, company_id in impacted:
            self.env["rn.color.rule.service"].recompute_model_tags(model_name, company_id=company_id)
        return result

    def _rn_recompute_impacted_models(self):
        self.env["rn.color.rule.service"].clear_rule_cache()
        if self.env.context.get("rn_skip_color_recompute"):
            return
        for rule in self:
            if not rule.model_name:
                _logger.debug("Skipping recompute for rule %s without model_name", rule.id)
                continue
            self.env["rn.color.rule.service"].recompute_model_tags(
                rule.model_name, company_id=rule.company_id.id
            )
