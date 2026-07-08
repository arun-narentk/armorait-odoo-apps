# -*- coding: utf-8 -*-
"""
Notification / WhatsApp message building and logging.
No credit risk logic; only message content, log creation, and chatter.
Error handling: try/except with logging, retry counter, fail-safe queue.
"""

import logging
from datetime import date

_logger = logging.getLogger(__name__)

# Max retries for failed notifications before giving up (configurable via env if needed)
MAX_RETRIES = 3


def build_overdue_invoice_message(move, delay_days):
    """
    Build the overdue reminder message body for an invoice.
    :param move: account.move (singleton)
    :param delay_days: int
    :return: str
    """
    return (
        'Dear %s,\n\n'
        'Your invoice %s of %s is overdue by %s days.\n\n'
        'Please arrange payment immediately.\n\n'
        'Regards,\nAccounts Team'
    ) % (
        move.partner_id.name or 'Customer',
        move.name,
        move.currency_id.format(move.amount_total),
        delay_days,
    )


def log_message_and_post_to_chatter(
    env, res_model, res_id, partner_id, message_body, company_id,
    state='sent', failure_reason=None, retry_count=0,
):
    """
    Create a whatsapp.message.log and post a note to the related record's chatter.
    :param env: Environment
    :param res_model: str
    :param res_id: int
    :param partner_id: int or False
    :param message_body: str
    :param company_id: int
    :param state: 'sent' | 'failed' | 'delivered'
    :param failure_reason: str or None
    :param retry_count: int (attempt number, 0 = first attempt)
    """
    Log = env['whatsapp.message.log']
    log = Log.create({
        'res_model': res_model,
        'res_id': res_id,
        'partner_id': partner_id,
        'state': state,
        'message_body': message_body,
        'failure_reason': failure_reason,
        'retry_count': retry_count,
        'company_id': company_id,
    })
    log._log_to_chatter()


def process_overdue_invoices_cron(env):
    """
    Find posted unpaid customer invoices overdue as of today, build message for each,
    create log and post to chatter. Fail-safe: one failure does not stop the rest;
    failures are logged and stored with state='failed' and retry_count=1.
    Skips if Settings → Enable WhatsApp Automation is disabled.
    :param env: Environment
    """
    ICP = env['ir.config_parameter'].sudo()
    if ICP.get_param('rn_smart_credit_shield.enable_whatsapp_automation', 'True') != 'True':
        return
    today = date.today()
    Move = env['account.move']
    overdue = Move.search([
        ('move_type', 'in', ('out_invoice', 'out_refund', 'out_receipt')),
        ('state', '=', 'posted'),
        ('payment_state', 'not in', ('paid', 'reversed')),
        ('invoice_date_due', '<', today),
    ])
    for move in overdue:
        try:
            delay_days = (today - move.invoice_date_due).days
            message_body = build_overdue_invoice_message(move, delay_days)
            log_message_and_post_to_chatter(
                env,
                res_model='account.move',
                res_id=move.id,
                partner_id=move.partner_id.id,
                message_body=message_body,
                company_id=move.company_id.id,
                state='sent',
                retry_count=0,
            )
        except Exception as e:
            _logger.exception(
                'WhatsApp overdue reminder failed for account.move %s (%s): %s',
                move.id, move.name, e,
            )
            try:
                log_message_and_post_to_chatter(
                    env,
                    res_model='account.move',
                    res_id=move.id,
                    partner_id=move.partner_id.id,
                    message_body='',
                    company_id=move.company_id.id,
                    state='failed',
                    failure_reason=str(e)[:500],
                    retry_count=1,
                )
            except Exception as e2:
                _logger.exception('Could not create failed log for move %s: %s', move.id, e2)
            # Continue to next move (fail-safe queue)


def retry_failed_messages(env, max_retries=None):
    """
    Retry failed WhatsApp logs whose retry_count is below max_retries.
    Fail-safe: one retry failure does not stop others.
    :param env: Environment
    :param max_retries: int or None (default MAX_RETRIES)
    """
    limit = max_retries if max_retries is not None else MAX_RETRIES
    Log = env['whatsapp.message.log']
    failed = Log.search([
        ('state', '=', 'failed'),
        ('retry_count', '<', limit),
    ])
    for log in failed:
        try:
            log.action_retry()
        except Exception as e:
            _logger.exception('Retry failed for whatsapp.message.log %s: %s', log.id, e)
