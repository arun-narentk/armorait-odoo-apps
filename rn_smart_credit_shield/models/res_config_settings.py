# -*- coding: utf-8 -*-

from odoo import api, fields, models

CREDIT_SHIELD_PARAMS = {
    'weight_overdue': 'rn_smart_credit_shield.credit_risk_weight_overdue_ratio',
    'weight_delay': 'rn_smart_credit_shield.credit_risk_weight_avg_delay',
    'weight_unpaid_count': 'rn_smart_credit_shield.credit_risk_weight_unpaid_count',
    'weight_exposure': 'rn_smart_credit_shield.credit_risk_weight_exposure',
    'threshold_medium': 'rn_smart_credit_shield.credit_risk_threshold_medium',
    'threshold_high': 'rn_smart_credit_shield.credit_risk_threshold_high',
    'threshold_critical': 'rn_smart_credit_shield.credit_risk_threshold_critical',
    'enable_auto_block': 'rn_smart_credit_shield.enable_auto_block',
    'enable_whatsapp_automation': 'rn_smart_credit_shield.enable_whatsapp_automation',
}


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    # Weights (0–100, normalized in logic)
    credit_risk_weight_overdue = fields.Float(
        string='Overdue Ratio Weight',
        default=40,
        help='Weight for overdue amount vs total receivable (0–100).',
    )
    credit_risk_weight_delay = fields.Float(
        string='Avg Delay Weight',
        default=30,
        help='Weight for average payment delay (0–100).',
    )
    credit_risk_weight_unpaid_count = fields.Float(
        string='Unpaid Count Weight',
        default=20,
        help='Weight for number of unpaid invoices (0–100).',
    )
    credit_risk_weight_exposure = fields.Float(
        string='Exposure Weight',
        default=10,
        help='Weight for exposure vs credit limit (0–100).',
    )
    # Thresholds (score 0–100: low < medium < high < critical)
    credit_risk_threshold_medium = fields.Float(
        string='Medium Threshold',
        default=30,
        help='Score >= this → Medium risk.',
    )
    credit_risk_threshold_high = fields.Float(
        string='High Threshold',
        default=60,
        help='Score >= this → High risk.',
    )
    credit_risk_threshold_critical = fields.Float(
        string='Critical Threshold',
        default=90,
        help='Score >= this → Critical risk.',
    )
    enable_auto_block = fields.Boolean(
        string='Enable Auto Block',
        default=True,
        help='Block SO confirmation for critical risk; require manager override for high risk.',
    )
    enable_whatsapp_automation = fields.Boolean(
        string='Enable WhatsApp Automation',
        default=True,
        help='Run daily overdue reminders and log to WhatsApp message log / chatter.',
    )

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        ICP = self.env['ir.config_parameter'].sudo()
        res.update(
            credit_risk_weight_overdue=float(ICP.get_param(CREDIT_SHIELD_PARAMS['weight_overdue'], 40)),
            credit_risk_weight_delay=float(ICP.get_param(CREDIT_SHIELD_PARAMS['weight_delay'], 30)),
            credit_risk_weight_unpaid_count=float(ICP.get_param(CREDIT_SHIELD_PARAMS['weight_unpaid_count'], 20)),
            credit_risk_weight_exposure=float(ICP.get_param(CREDIT_SHIELD_PARAMS['weight_exposure'], 10)),
            credit_risk_threshold_medium=float(ICP.get_param(CREDIT_SHIELD_PARAMS['threshold_medium'], 30)),
            credit_risk_threshold_high=float(ICP.get_param(CREDIT_SHIELD_PARAMS['threshold_high'], 60)),
            credit_risk_threshold_critical=float(ICP.get_param(CREDIT_SHIELD_PARAMS['threshold_critical'], 90)),
            enable_auto_block=ICP.get_param(CREDIT_SHIELD_PARAMS['enable_auto_block'], 'True') == 'True',
            enable_whatsapp_automation=ICP.get_param(CREDIT_SHIELD_PARAMS['enable_whatsapp_automation'], 'True') == 'True',
        )
        return res

    def set_values(self):
        super(ResConfigSettings, self).set_values()
        ICP = self.env['ir.config_parameter'].sudo()
        ICP.set_param(CREDIT_SHIELD_PARAMS['weight_overdue'], str(round(self.credit_risk_weight_overdue, 2)))
        ICP.set_param(CREDIT_SHIELD_PARAMS['weight_delay'], str(round(self.credit_risk_weight_delay, 2)))
        ICP.set_param(CREDIT_SHIELD_PARAMS['weight_unpaid_count'], str(round(self.credit_risk_weight_unpaid_count, 2)))
        ICP.set_param(CREDIT_SHIELD_PARAMS['weight_exposure'], str(round(self.credit_risk_weight_exposure, 2)))
        ICP.set_param(CREDIT_SHIELD_PARAMS['threshold_medium'], str(round(self.credit_risk_threshold_medium, 2)))
        ICP.set_param(CREDIT_SHIELD_PARAMS['threshold_high'], str(round(self.credit_risk_threshold_high, 2)))
        ICP.set_param(CREDIT_SHIELD_PARAMS['threshold_critical'], str(round(self.credit_risk_threshold_critical, 2)))
        ICP.set_param(CREDIT_SHIELD_PARAMS['enable_auto_block'], str(self.enable_auto_block))
        ICP.set_param(CREDIT_SHIELD_PARAMS['enable_whatsapp_automation'], str(self.enable_whatsapp_automation))
