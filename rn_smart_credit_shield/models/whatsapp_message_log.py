# -*- coding: utf-8 -*-

import logging

from odoo import fields, models

_logger = logging.getLogger(__name__)


class WhatsAppMessageLog(models.Model):
    _name = 'whatsapp.message.log'
    _description = 'WhatsApp Message Log'
    _order = 'create_date desc'

    res_model = fields.Char(string='Related Model', index=True)
    res_id = fields.Integer(string='Related Document ID', index=True)
    partner_id = fields.Many2one('res.partner', string='Contact', ondelete='set null')
    state = fields.Selection(
        [('sent', 'Sent'), ('failed', 'Failed'), ('delivered', 'Delivered')],
        string='Status',
        default='sent',
        required=True,
    )
    message_body = fields.Text(string='Message')
    failure_reason = fields.Char(string='Failure Reason')
    error_message = fields.Char(string='Error Message', help='Same as Failure Reason; for API clarity.')
    retry_count = fields.Integer(string='Retry Count', default=0, help='Number of send attempts including retries.')
    last_attempt = fields.Datetime(string='Last Attempt', default=fields.Datetime.now, readonly=True, help='Last time a send/retry was attempted.')
    company_id = fields.Many2one('res.company', default=lambda self: self.env.company)

    def _log_to_chatter(self):
        for log in self:
            if not log.res_model or not log.res_id:
                continue
            try:
                record = self.env[log.res_model].browse(log.res_id).exists()
                if not record or not hasattr(record, 'message_post'):
                    continue
                body = 'WhatsApp: %s\n%s' % (log.state, (log.message_body or '')[:300])
                if log.failure_reason:
                    body += '\nFailure: %s' % log.failure_reason
                record.message_post(body=body, message_type='notification', subtype_xmlid='mail.mt_note')
            except Exception as e:
                _logger.exception(
                    'WhatsApp log chatter post failed for %s/%s: %s',
                    log.res_model, log.res_id, e,
                )
                log.write({'state': 'failed', 'failure_reason': str(e)[:500]})

    def action_retry(self):
        """Re-attempt posting to chatter for failed logs. Increments retry_count."""
        for log in self:
            if log.state != 'failed':
                continue
            log.retry_count += 1
            try:
                if log.res_model and log.res_id:
                    record = self.env[log.res_model].browse(log.res_id).exists()
                    if record and hasattr(record, 'message_post'):
                        body = 'WhatsApp (retry %s): %s\n%s' % (
                            log.retry_count, log.state, (log.message_body or '')[:300]
                        )
                        if log.failure_reason:
                            body += '\nPrevious failure: %s' % log.failure_reason
                        record.message_post(body=body, message_type='notification', subtype_xmlid='mail.mt_note')
                log.write({'state': 'sent', 'failure_reason': False, 'last_attempt': fields.Datetime.now()})
            except Exception as e:
                _logger.exception(
                    'WhatsApp retry failed for %s/%s (retry %s): %s',
                    log.res_model, log.res_id, log.retry_count, e,
                )
                log.write({'failure_reason': str(e)[:500], 'last_attempt': fields.Datetime.now()})
