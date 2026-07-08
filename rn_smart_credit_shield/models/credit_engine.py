# -*- coding: utf-8 -*-
"""
Credit risk aggregation and score computation, service layer (no Odoo model).
Uses risk_utils for config; no notification/WhatsApp logic here.
Reusable in cron, SO confirmation, and partner compute.
"""

from datetime import date

from odoo.tools import float_round

from . import risk_utils


def _get_aggregates_sql(env, commercial_partner_ids, company_id, today=None):
    """
    One SQL aggregation for unpaid/overdue metrics per commercial partner.
    :return: dict commercial_partner_id -> {total_residual, overdue_residual, unpaid_count, overdue_count, total_delay_days}
    """
    if not commercial_partner_ids:
        return {}
    today = today or date.today()
    env['account.move'].flush_model([
        'commercial_partner_id', 'company_id', 'state', 'payment_state', 'move_type',
        'invoice_date_due', 'amount_residual',
    ])
    today_str = today.isoformat()
    env.cr.execute("""
        SELECT
            commercial_partner_id,
            COALESCE(SUM(amount_residual), 0) AS total_residual,
            COALESCE(SUM(CASE WHEN invoice_date_due IS NOT NULL AND invoice_date_due < %s
                THEN amount_residual ELSE 0 END), 0) AS overdue_residual,
            COUNT(*) AS unpaid_count,
            COALESCE(SUM(CASE WHEN invoice_date_due IS NOT NULL AND invoice_date_due < %s THEN 1 ELSE 0 END), 0)::int AS overdue_count,
            COALESCE(SUM(CASE WHEN invoice_date_due IS NOT NULL AND invoice_date_due < %s
                THEN (%s::date - invoice_date_due) ELSE 0 END), 0)::int AS total_delay_days
        FROM account_move
        WHERE state = 'posted'
          AND payment_state NOT IN ('paid', 'reversed')
          AND move_type IN ('out_invoice', 'out_refund', 'out_receipt')
          AND company_id = %s
          AND commercial_partner_id = ANY(%s)
        GROUP BY commercial_partner_id
    """, (today_str, today_str, today_str, today_str, company_id, commercial_partner_ids))
    rows = env.cr.dictfetchall()
    return {
        row['commercial_partner_id']: {
            'total_residual': float(row['total_residual']),
            'overdue_residual': float(row['overdue_residual']),
            'unpaid_count': row['unpaid_count'],
            'overdue_count': row['overdue_count'],
            'total_delay_days': row['total_delay_days'] or 0,
        }
        for row in rows
    }


def _compute_risk_results(aggregates, credit_limits, weights, thresholds):
    """
    From aggregates and credit limits, compute score, level, and avg_delay per commercial partner.
    :return: dict commercial_partner_id -> {'score': float, 'level': str, 'avg_delay': float}
    """
    w_overdue = weights.get('overdue', 40)
    w_delay = weights.get('delay', 30)
    w_count = weights.get('unpaid_count', 20)
    w_exposure = weights.get('exposure', 10)
    total_weight = w_overdue + w_delay + w_count + w_exposure
    if total_weight <= 0:
        total_weight = 100.0

    result = {}
    for commercial_id, agg in aggregates.items():
        total_receivable = agg['total_residual']
        overdue_amount = agg['overdue_residual']
        unpaid_count = agg['unpaid_count']
        overdue_count = agg['overdue_count']
        total_delay_days = agg['total_delay_days']

        overdue_ratio = (overdue_amount / total_receivable * 100.0) if total_receivable else 0.0
        overdue_ratio = min(100.0, overdue_ratio)

        avg_delay = total_delay_days / overdue_count if overdue_count else 0.0
        delay_score = min(100.0, avg_delay * 2.0)
        count_score = min(100.0, unpaid_count * 10.0)

        credit_limit = credit_limits.get(commercial_id, 0.0)
        if credit_limit and credit_limit > 0:
            exposure_ratio = (total_receivable / credit_limit) * 100.0
            exposure_score = min(100.0, exposure_ratio)
        elif total_receivable > 0:
            exposure_score = 50.0
        else:
            exposure_score = 0.0

        score = (
            overdue_ratio * (w_overdue / total_weight) +
            delay_score * (w_delay / total_weight) +
            count_score * (w_count / total_weight) +
            exposure_score * (w_exposure / total_weight)
        )
        score = float_round(score, precision_digits=2)
        level = risk_utils.score_to_level(score, thresholds)

        result[commercial_id] = {
            'score': score,
            'level': level,
            'avg_delay': float_round(avg_delay, precision_digits=2),
        }
    return result


class CreditRiskEngine:
    """
    Service-style credit risk engine (not an Odoo model).
    Use for testing, cron, SO confirmation, and partner compute.
    """

    @staticmethod
    def compute_partner_risk(env, partner):
        """
        Compute credit risk for a single partner (e.g. at SO confirmation).
        :param env: Environment
        :param partner: res.partner (singleton, typically commercial partner)
        :return: dict {'score': float, 'level': str, 'avg_delay': float} or None if no data
        """
        partner = partner.commercial_partner_id
        company_id = env.company.id
        commercial_ids = [partner.id]
        today = date.today()
        aggregates = _get_aggregates_sql(env, commercial_ids, company_id, today)
        if not aggregates:
            return {'score': 0.0, 'level': 'low', 'avg_delay': 0.0}
        credit_limits = {partner.id: (partner.credit_limit or 0.0)}
        weights = risk_utils.get_risk_weights(env)
        thresholds = risk_utils.get_risk_thresholds(env)
        results = _compute_risk_results(aggregates, credit_limits, weights, thresholds)
        return results.get(partner.id, {'score': 0.0, 'level': 'low', 'avg_delay': 0.0})

    @staticmethod
    def compute_risk_for_partners(env, partners):
        """
        Batch compute credit risk for multiple partners (e.g. res.partner _compute_credit_risk).
        :param env: Environment
        :param partners: recordset of res.partner
        :return: dict commercial_partner_id -> {'score': float, 'level': str, 'avg_delay': float}
        """
        if not partners:
            return {}
        today = date.today()
        company_id = env.company.id
        commercial_ids = list(set(partners.mapped('commercial_partner_id').ids))
        aggregates = _get_aggregates_sql(env, commercial_ids, company_id, today)
        if not aggregates:
            return {}
        commercial_partners = env['res.partner'].browse(commercial_ids)
        credit_limits = {p.id: (p.credit_limit or 0.0) for p in commercial_partners}
        weights = risk_utils.get_risk_weights(env)
        thresholds = risk_utils.get_risk_thresholds(env)
        return _compute_risk_results(aggregates, credit_limits, weights, thresholds)


# Backward compatibility: module-level functions delegate to engine
def get_aggregates_sql(env, commercial_partner_ids, company_id, today=None):
    return _get_aggregates_sql(env, commercial_partner_ids, company_id, today)


def compute_risk_results(aggregates, credit_limits, weights, thresholds):
    return _compute_risk_results(aggregates, credit_limits, weights, thresholds)
