# -*- coding: utf-8 -*-
"""Follow-up automation runner."""

import logging

from odoo import fields, models

_logger = logging.getLogger(__name__)


class RnCrmFollowupService(models.AbstractModel):
    """Create reminders and escalations from follow-up rules."""

    _name = 'rn.crm.followup.service'
    _description = 'CRM Follow-up Service'

    def run_rules(self):
        """Evaluate active follow-up rules (expanded in later phase)."""
        rules = self.env['rn.crm.followup.rule'].search([('active', '=', True)])
        Reminder = self.env['rn.crm.reminder']
        count = 0
        for rule in rules:
            # Phase 3: select aging / inactive leads per trigger.
            Reminder.create({
                'name': 'Follow-up: %s' % rule.name,
                'schedule_at': fields.Datetime.now(),
                'channel': 'activity',
                'body': 'Automated follow-up from rule %s' % rule.name,
            })
            count += 1
        _logger.info('Follow-up rules processed=%s', count)
        return count
