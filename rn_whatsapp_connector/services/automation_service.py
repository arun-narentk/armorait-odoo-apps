# -*- coding: utf-8 -*-
"""Generic automation engine for WhatsApp triggers."""

import logging
from datetime import timedelta

from odoo import fields, models
from odoo.tools.safe_eval import safe_eval

_logger = logging.getLogger(__name__)


class RnWhatsappAutomationService(models.AbstractModel):
    """Run registered automation rules for a trigger and set of records."""

    _name = 'rn.whatsapp.automation.service'
    _description = 'WhatsApp Automation Service'

    # Extra triggers can be registered by other modules at runtime
    EXTRA_TRIGGERS = {}

    def register_trigger(self, key, label):
        self.EXTRA_TRIGGERS[key] = label
        return True

    def run_trigger(self, trigger, records):
        if not records:
            return self.env['rn.whatsapp.message']
        company_ids = records.mapped('company_id').ids if 'company_id' in records._fields else [self.env.company.id]
        domain = [
            ('active', '=', True),
            ('trigger', '=', trigger),
            ('company_id', 'in', company_ids or [self.env.company.id]),
        ]
        rules = self.env['rn.whatsapp.automation.rule'].sudo().search(domain)
        created = self.env['rn.whatsapp.message']
        for rule in rules:
            for record in records:
                if rule.model_name and record._name != rule.model_name:
                    continue
                if not self._match_domain(record, rule.domain):
                    continue
                if rule.trigger == 'state_changed' and rule.state_field and rule.state_value:
                    if str(getattr(record, rule.state_field, '')) != str(rule.state_value):
                        continue
                message = self._queue_for_record(rule, record)
                if message:
                    created |= message
        _logger.info('Automation %s created %s messages', trigger, len(created))
        return created

    def _match_domain(self, record, domain_str):
        domain = safe_eval(domain_str or '[]')
        if not domain:
            return True
        return bool(record.filtered_domain(domain))

    def _resolve_path(self, record, path):
        if not path:
            return False
        current = record
        for part in path.split('.'):
            if not current:
                return False
            current = current[part] if part in current._fields else False
            if isinstance(current, models.Model) and len(current) > 1:
                current = current[:1]
        return current

    def _queue_for_record(self, rule, record):
        phone_value = self._resolve_path(record, rule.phone_field or 'partner_id.mobile')
        if not phone_value:
            phone_value = self._resolve_path(record, 'partner_id.phone')
        phone = phone_value if isinstance(phone_value, str) else (phone_value or '')
        if hasattr(phone, 'strip'):
            phone = phone.strip()
        if not phone:
            _logger.info('Skip automation %s: no phone on %s,%s', rule.name, record._name, record.id)
            return False
        partner = self._resolve_path(record, rule.partner_field or 'partner_id')
        if isinstance(partner, models.Model):
            partner = partner[:1]
        else:
            partner = self.env['res.partner']
        var_names = [v.strip() for v in (rule.template_id.variable_ids or 'name,partner').split(',') if v.strip()]
        variables = self.env['rn.whatsapp.template.service'].extract_record_vars(record, var_names)
        schedule_at = False
        if rule.delay_minutes:
            schedule_at = fields.Datetime.now() + timedelta(minutes=rule.delay_minutes)
        message = self.env['rn.whatsapp.message.service'].build_template_message(
            rule.account_id,
            phone,
            rule.template_id,
            variables=variables,
            partner=partner,
            automation_rule_id=rule.id,
            res_model=record._name,
            res_id=record.id,
            schedule_at=schedule_at,
            status='queued',
        )
        if not schedule_at:
            self.env['rn.whatsapp.message.service'].send_messages(message)
        return message
