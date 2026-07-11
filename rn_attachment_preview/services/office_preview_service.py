# -*- coding: utf-8 -*-
"""Office document HTML preview without external Office licenses."""

from __future__ import annotations

import io
import logging
import re
import zipfile
import xml.etree.ElementTree as ET

from odoo import api, models
from odoo.tools import html_escape

from ..constants import OFFICE_MIMETYPES

_logger = logging.getLogger(__name__)

_W_NS = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
_S_NS = {'main': 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
_P_NS = {'a': 'http://schemas.openxmlformats.org/drawingml/2006/main',
         'p': 'http://schemas.openxmlformats.org/presentationml/2006/main'}


class RnAttachmentOfficeService(models.AbstractModel):
    _name = 'rn.attachment.office.service'
    _description = 'Attachment Office Preview Service'

    @api.model
    def classify_office(self, mimetype: str | None) -> str | None:
        mapping = {
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document': 'word',
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': 'excel',
            'application/vnd.openxmlformats-officedocument.presentationml.presentation': 'powerpoint',
        }
        return mapping.get((mimetype or '').lower())

    @api.model
    def extract_plain_text(self, raw: bytes, mimetype: str) -> str:
        office_type = self.classify_office(mimetype)
        if office_type == 'word':
            return self._extract_docx_text(raw)
        if office_type == 'excel':
            return self._extract_xlsx_text(raw)
        if office_type == 'powerpoint':
            return self._extract_pptx_text(raw)
        return ''

    @api.model
    def build_preview_html(self, attachment) -> str:
        attachment.ensure_one()
        raw = attachment.raw or b''
        mimetype = (attachment.mimetype or '').lower()
        office_type = self.classify_office(mimetype)
        if office_type == 'word':
            return self._render_docx_html(raw, attachment.name)
        if office_type == 'excel':
            return self._render_xlsx_html(raw, attachment.name)
        if office_type == 'powerpoint':
            return self._render_pptx_html(raw, attachment.name)
        return self._render_fallback_html(attachment.name, mimetype)

    @api.model
    def process_attachment(self, attachment) -> bool:
        attachment.ensure_one()
        mimetype = (attachment.mimetype or '').lower()
        if mimetype not in OFFICE_MIMETYPES:
            return False
        html_preview = self.build_preview_html(attachment)
        attachment.sudo().write({'rn_office_preview_html': html_preview})
        return True

    @api.model
    def _extract_docx_text(self, raw: bytes) -> str:
        try:
            with zipfile.ZipFile(io.BytesIO(raw)) as archive:
                xml_data = archive.read('word/document.xml')
            root = ET.fromstring(xml_data)
            chunks = [node.text for node in root.findall('.//w:t', _W_NS) if node.text]
            return ' '.join(chunks)[:50000]
        except Exception as exc:  # noqa: BLE001
            _logger.warning('DOCX text extract failed: %s', exc)
            return ''

    @api.model
    def _extract_xlsx_text(self, raw: bytes) -> str:
        try:
            with zipfile.ZipFile(io.BytesIO(raw)) as archive:
                shared = []
                if 'xl/sharedStrings.xml' in archive.namelist():
                    shared_root = ET.fromstring(archive.read('xl/sharedStrings.xml'))
                    for item in shared_root.findall('.//main:si', _S_NS):
                        texts = [node.text for node in item.findall('.//main:t', _S_NS) if node.text]
                        shared.append(''.join(texts))
                sheet_name = next((n for n in archive.namelist() if n.startswith('xl/worksheets/sheet')), None)
                if not sheet_name:
                    return ' '.join(shared)[:50000]
                sheet_root = ET.fromstring(archive.read(sheet_name))
                values = []
                for cell in sheet_root.findall('.//main:c', _S_NS):
                    cell_type = cell.get('t')
                    value_node = cell.find('main:v', _S_NS)
                    if value_node is None or value_node.text is None:
                        continue
                    if cell_type == 's':
                        idx = int(value_node.text)
                        values.append(shared[idx] if idx < len(shared) else '')
                    else:
                        values.append(value_node.text)
                return ' '.join(values)[:50000]
        except Exception as exc:  # noqa: BLE001
            _logger.warning('XLSX text extract failed: %s', exc)
            return ''

    @api.model
    def _extract_pptx_text(self, raw: bytes) -> str:
        try:
            texts = []
            with zipfile.ZipFile(io.BytesIO(raw)) as archive:
                slide_files = sorted(
                    name for name in archive.namelist()
                    if name.startswith('ppt/slides/slide') and name.endswith('.xml')
                )
                for slide_file in slide_files[:20]:
                    root = ET.fromstring(archive.read(slide_file))
                    for node in root.findall('.//a:t', _P_NS):
                        if node.text:
                            texts.append(node.text)
            return ' '.join(texts)[:50000]
        except Exception as exc:  # noqa: BLE001
            _logger.warning('PPTX text extract failed: %s', exc)
            return ''

    @api.model
    def _render_docx_html(self, raw: bytes, name: str | None) -> str:
        paragraphs = re.split(r'\s{2,}|\n+', self._extract_docx_text(raw))
        body = ''.join(
            f'<p>{html_escape(chunk.strip())}</p>'
            for chunk in paragraphs if chunk.strip()
        ) or '<p><em>No readable text found in this document.</em></p>'
        return self._wrap_html(name, 'Word Preview', body)

    @api.model
    def _render_xlsx_html(self, raw: bytes, name: str | None) -> str:
        try:
            with zipfile.ZipFile(io.BytesIO(raw)) as archive:
                shared = []
                if 'xl/sharedStrings.xml' in archive.namelist():
                    shared_root = ET.fromstring(archive.read('xl/sharedStrings.xml'))
                    for item in shared_root.findall('.//main:si', _S_NS):
                        texts = [node.text for node in item.findall('.//main:t', _S_NS) if node.text]
                        shared.append(''.join(texts))
                sheet_name = next((n for n in archive.namelist() if n.startswith('xl/worksheets/sheet')), None)
                rows_html = []
                if sheet_name:
                    sheet_root = ET.fromstring(archive.read(sheet_name))
                    row_nodes = sheet_root.findall('.//main:row', _S_NS)[:30]
                    for row in row_nodes:
                        cells = []
                        for cell in row.findall('main:c', _S_NS)[:12]:
                            cell_type = cell.get('t')
                            value_node = cell.find('main:v', _S_NS)
                            value = ''
                            if value_node is not None and value_node.text is not None:
                                if cell_type == 's':
                                    idx = int(value_node.text)
                                    value = shared[idx] if idx < len(shared) else ''
                                else:
                                    value = value_node.text
                            cells.append(f'<td>{html_escape(value)}</td>')
                        if cells:
                            rows_html.append(f'<tr>{"".join(cells)}</tr>')
                body = (
                    '<table class="table table-sm table-bordered">'
                    f'{"".join(rows_html)}'
                    '</table>'
                ) if rows_html else '<p><em>No sheet rows found.</em></p>'
                return self._wrap_html(name, 'Excel Preview', body)
        except Exception as exc:  # noqa: BLE001
            _logger.warning('XLSX preview failed: %s', exc)
            return self._render_fallback_html(name, 'excel')

    @api.model
    def _render_pptx_html(self, raw: bytes, name: str | None) -> str:
        slides = []
        try:
            with zipfile.ZipFile(io.BytesIO(raw)) as archive:
                slide_files = sorted(
                    name for name in archive.namelist()
                    if name.startswith('ppt/slides/slide') and name.endswith('.xml')
                )
                for index, slide_file in enumerate(slide_files[:12], start=1):
                    root = ET.fromstring(archive.read(slide_file))
                    texts = [node.text for node in root.findall('.//a:t', _P_NS) if node.text]
                    slide_body = '<br/>'.join(html_escape(text) for text in texts) or '<em>Empty slide</em>'
                    slides.append(
                        f'<div class="rn_office_slide"><h5>Slide {index}</h5><p>{slide_body}</p></div>'
                    )
        except Exception as exc:  # noqa: BLE001
            _logger.warning('PPTX preview failed: %s', exc)
            return self._render_fallback_html(name, 'powerpoint')
        body = ''.join(slides) or '<p><em>No slides found.</em></p>'
        return self._wrap_html(name, 'PowerPoint Preview', body)

    @api.model
    def _render_fallback_html(self, name: str | None, mimetype: str) -> str:
        body = (
            f'<p>Preview is not available for <strong>{html_escape(name or "file")}</strong>.</p>'
            '<p>Download the file to open it in Office.</p>'
        )
        return self._wrap_html(name, 'Office Document', body)

    @api.model
    def _wrap_html(self, name: str | None, title: str, body: str) -> str:
        return (
            f'<div class="rn_office_preview"><h4>{html_escape(title)}</h4>'
            f'<p class="text-muted">{html_escape(name or "")}</p>{body}</div>'
        )
