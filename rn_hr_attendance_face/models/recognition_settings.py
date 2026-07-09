# -*- coding: utf-8 -*-
"""Company-wide recognition and attendance rule settings."""

from odoo import fields, models


class RnHrRecognitionSettings(models.Model):
    """Per-company face recognition thresholds and engine choices."""

    _name = 'rn.hr.recognition.settings'
    _description = 'Face Recognition Settings'
    _inherit = ['mail.thread']

    name = fields.Char(required=True, default='Recognition Settings')
    company_id = fields.Many2one(
        'res.company',
        required=True,
        default=lambda self: self.env.company,
    )
    matching_threshold = fields.Float(
        string='Matching Threshold',
        default=0.45,
        help='Cosine distance / similarity cutoff for accepting a match.',
    )
    minimum_confidence = fields.Float(string='Minimum Confidence', default=0.70)
    min_face_size = fields.Integer(string='Minimum Face Size (px)', default=80)
    detection_model = fields.Selection(
        selection=[
            ('opencv', 'OpenCV Haar/DNN'),
            ('insightface', 'InsightFace'),
            ('onnx', 'ONNX Runtime'),
        ],
        default='opencv',
        required=True,
    )
    embedding_model = fields.Selection(
        selection=[
            ('insightface', 'InsightFace'),
            ('facenet', 'FaceNet'),
            ('onnx', 'ONNX Runtime'),
        ],
        default='insightface',
        required=True,
    )
    anti_spoof_enabled = fields.Boolean(string='Anti Spoof Enabled', default=True)
    geo_validation = fields.Boolean(string='Geo Validation', default=False)
    camera_timeout = fields.Integer(string='Camera Timeout (s)', default=15)
    retry_count = fields.Integer(string='Retry Count', default=3)
    min_enrollment_images = fields.Integer(string='Minimum Enrollment Images', default=10)
    target_recognition_ms = fields.Integer(string='Target Recognition Time (ms)', default=500)
    grace_time_minutes = fields.Integer(string='Grace Time (minutes)', default=10)
    store_snapshots = fields.Boolean(
        string='Store Failure Snapshots',
        default=True,
        help='Keep images for unknown/spoof attempts only.',
    )
    active = fields.Boolean(default=True)

    _company_uniq = models.Constraint(
        'unique(company_id)',
        'Only one recognition settings record per company.',
    )
