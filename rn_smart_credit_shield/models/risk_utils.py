# -*- coding: utf-8 -*-
"""
Shared risk configuration and score-to-level mapping.
Used by credit_engine and any feature that needs thresholds/weights.
"""

from datetime import date


# Config parameter keys (single source of truth)
KEY_WEIGHT_OVERDUE = 'rn_smart_credit_shield.credit_risk_weight_overdue_ratio'
KEY_WEIGHT_DELAY = 'rn_smart_credit_shield.credit_risk_weight_avg_delay'
KEY_WEIGHT_UNPAID_COUNT = 'rn_smart_credit_shield.credit_risk_weight_unpaid_count'
KEY_WEIGHT_EXPOSURE = 'rn_smart_credit_shield.credit_risk_weight_exposure'
KEY_THRESHOLD_MEDIUM = 'rn_smart_credit_shield.credit_risk_threshold_medium'
KEY_THRESHOLD_HIGH = 'rn_smart_credit_shield.credit_risk_threshold_high'
KEY_THRESHOLD_CRITICAL = 'rn_smart_credit_shield.credit_risk_threshold_critical'

DEFAULT_WEIGHTS = {
    'overdue': 40.0,
    'delay': 30.0,
    'unpaid_count': 20.0,
    'exposure': 10.0,
}
DEFAULT_THRESHOLDS = {
    'medium': 30.0,
    'high': 60.0,
    'critical': 90.0,
}


def get_risk_weights(env):
    """Return risk score weights from ir.config_parameter (overdue, delay, unpaid_count, exposure)."""
    ICP = env['ir.config_parameter'].sudo()
    return {
        'overdue': float(ICP.get_param(KEY_WEIGHT_OVERDUE, DEFAULT_WEIGHTS['overdue'])),
        'delay': float(ICP.get_param(KEY_WEIGHT_DELAY, DEFAULT_WEIGHTS['delay'])),
        'unpaid_count': float(ICP.get_param(KEY_WEIGHT_UNPAID_COUNT, DEFAULT_WEIGHTS['unpaid_count'])),
        'exposure': float(ICP.get_param(KEY_WEIGHT_EXPOSURE, DEFAULT_WEIGHTS['exposure'])),
    }


def get_risk_thresholds(env):
    """Return risk level thresholds from ir.config_parameter (medium, high, critical)."""
    ICP = env['ir.config_parameter'].sudo()
    return {
        'medium': float(ICP.get_param(KEY_THRESHOLD_MEDIUM, DEFAULT_THRESHOLDS['medium'])),
        'high': float(ICP.get_param(KEY_THRESHOLD_HIGH, DEFAULT_THRESHOLDS['high'])),
        'critical': float(ICP.get_param(KEY_THRESHOLD_CRITICAL, DEFAULT_THRESHOLDS['critical'])),
    }


def score_to_level(score, thresholds):
    """
    Map numeric score (0–100) to risk level.
    :param score: float
    :param thresholds: dict with 'medium', 'high', 'critical' (float)
    :return: 'low' | 'medium' | 'high' | 'critical'
    """
    if score < thresholds.get('medium', DEFAULT_THRESHOLDS['medium']):
        return 'low'
    if score < thresholds.get('high', DEFAULT_THRESHOLDS['high']):
        return 'medium'
    if score < thresholds.get('critical', DEFAULT_THRESHOLDS['critical']):
        return 'high'
    return 'critical'
