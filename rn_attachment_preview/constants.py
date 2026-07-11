# -*- coding: utf-8 -*-
"""Constants for rn_attachment_preview."""

PREVIEWABLE_MIMETYPES = {
    'application/pdf',
    'image/bmp',
    'image/gif',
    'image/jpeg',
    'image/png',
    'image/svg+xml',
    'image/webp',
    'image/x-icon',
    'video/mp4',
    'video/webm',
    'video/quicktime',
    'video/x-msvideo',
    'audio/mpeg',
    'audio/wav',
    'audio/ogg',
    'audio/webm',
    'text/plain',
    'text/csv',
    'text/xml',
    'application/xml',
    'application/json',
    'text/html',
}

TEXT_MIMETYPES = {
    'text/plain',
    'text/csv',
    'text/xml',
    'application/xml',
    'application/json',
    'text/html',
    'application/javascript',
}

IMAGE_MIMETYPES = {
    'image/bmp',
    'image/gif',
    'image/jpeg',
    'image/png',
    'image/svg+xml',
    'image/webp',
    'image/x-icon',
}

VIDEO_MIMETYPES = {
    'video/mp4',
    'video/webm',
    'video/quicktime',
    'video/x-msvideo',
}

AUDIO_MIMETYPES = {
    'audio/mpeg',
    'audio/wav',
    'audio/ogg',
    'audio/webm',
}

HOVER_PREVIEW_MAX_BYTES = 5 * 1024 * 1024
THUMBNAIL_MAX_BYTES = 10 * 1024 * 1024
OCR_MAX_BYTES = 15 * 1024 * 1024
THUMBNAIL_SIZE = (160, 160)
CRON_BATCH_SIZE = 40

OFFICE_MIMETYPES = {
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    'application/vnd.openxmlformats-officedocument.presentationml.presentation',
}

OCR_MIMETYPES = PREVIEWABLE_MIMETYPES | OFFICE_MIMETYPES

THUMBNAIL_MIMETYPES = IMAGE_MIMETYPES | {'application/pdf'} | OFFICE_MIMETYPES
