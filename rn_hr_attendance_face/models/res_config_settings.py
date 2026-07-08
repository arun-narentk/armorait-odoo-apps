# -*- coding: utf-8 -*-
"""System settings bridge for face attendance."""

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    """Expose module toggles on the Settings app."""

    _inherit = 'res.config.settings'

    rn_face_enabled = fields.Boolean(
        string='Enable Face Recognition Attendance',
        config_parameter='rn_hr_attendance_face.enabled',
    )
    rn_face_anti_spoof = fields.Boolean(
        string='Enable Anti Spoofing',
        config_parameter='rn_hr_attendance_face.anti_spoof',
        default=True,
    )
    rn_face_geo_validation = fields.Boolean(
        string='Enable Geo Validation',
        config_parameter='rn_hr_attendance_face.geo_validation',
    )
    rn_face_min_enrollment_images = fields.Integer(
        string='Minimum Enrollment Images',
        config_parameter='rn_hr_attendance_face.min_enrollment_images',
        default=10,
    )
    rn_face_matching_threshold = fields.Float(
        string='Default Matching Threshold',
        config_parameter='rn_hr_attendance_face.matching_threshold',
        default=0.45,
    )
    rn_face_detection_model = fields.Selection(
        selection=[
            ('opencv', 'OpenCV'),
            ('insightface', 'InsightFace'),
            ('onnx', 'ONNX Runtime'),
        ],
        string='Detection Model',
        config_parameter='rn_hr_attendance_face.detection_model',
        default='opencv',
    )
    rn_face_embedding_model = fields.Selection(
        selection=[
            ('insightface', 'InsightFace'),
            ('facenet', 'FaceNet'),
            ('onnx', 'ONNX Runtime'),
        ],
        string='Embedding Model',
        config_parameter='rn_hr_attendance_face.embedding_model',
        default='insightface',
    )
