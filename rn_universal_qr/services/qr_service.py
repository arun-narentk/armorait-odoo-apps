# -*- coding: utf-8 -*-
import base64
import io
import json
import zipfile

from odoo import fields, models
from odoo.exceptions import UserError

try:
    import qrcode
except ImportError:
    qrcode = None

try:
    import qrcode.image.svg
except ImportError:
    qrcode = None


class QrService(models.AbstractModel):
    _name = 'rn.qr.service'
    _description = 'Universal QR Service'

    def _build_token_url(self, token):
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        return f'{base_url}/rn/qr/{token}'

    def _check_qrcode_library(self):
        if not qrcode:
            raise UserError('Python package "qrcode" is required.')

    def generate_png(self, token):
        self._check_qrcode_library()
        url = self._build_token_url(token)
        image = qrcode.make(url)
        stream = io.BytesIO()
        image.save(stream, format='PNG')
        return base64.b64encode(stream.getvalue()), url

    def generate_svg(self, token):
        self._check_qrcode_library()
        url = self._build_token_url(token)
        factory = qrcode.image.svg.SvgPathImage
        image = qrcode.make(url, image_factory=factory)
        stream = io.BytesIO()
        image.save(stream)
        return stream.getvalue().decode('utf-8'), url

    def ensure_qr_record(self, business_record):
        qr_record = self.env['rn.qr.record'].search(
            [('res_model', '=', business_record._name), ('res_id', '=', business_record.id)],
            limit=1,
        )
        if qr_record:
            return qr_record
        template_id = int(
            self.env['ir.config_parameter'].sudo().get_param('rn_universal_qr.default_template_id', default='0') or 0
        )
        company = business_record.company_id if 'company_id' in business_record._fields else self.env.company
        return self.env['rn.qr.record'].create({
            'name': business_record.display_name,
            'token': business_record.rn_qr_token,
            'res_model': business_record._name,
            'res_id': business_record.id,
            'company_id': company.id,
            'template_id': template_id or False,
        })

    def export_bulk_zip(self, records, filename='qr_codes.zip'):
        zip_stream = io.BytesIO()
        payload_list = []
        with zipfile.ZipFile(zip_stream, mode='w', compression=zipfile.ZIP_DEFLATED) as archive:
            for record in records:
                record.action_generate_qr()
                safe_name = f"{record._name.replace('.', '_')}_{record.id}"
                image_data = base64.b64decode(record.rn_qr_image or b'')
                archive.writestr(f'{safe_name}.png', image_data)
                payload_list.append({
                    'name': record.display_name,
                    'model': record._name,
                    'id': record.id,
                    'token': record.rn_qr_token,
                    'url': record.rn_qr_url,
                    'generated_at': fields.Datetime.now().isoformat(),
                })
            archive.writestr('manifest.json', json.dumps(payload_list, indent=2))
        return {
            'filename': filename,
            'content': base64.b64encode(zip_stream.getvalue()),
        }

# -*- coding: utf-8 -*-
"""QR generation, rendering, and download helpers."""

import base64
import io
import logging
from datetime import timedelta

import qrcode
from PIL import Image

from odoo import api, fields, models, _
from odoo.exceptions import UserError

from odoo.addons.rn_universal_qr import constants

_logger = logging.getLogger(__name__)


class RnQrService(models.AbstractModel):
    _name = 'rn.qr.service'
    _description = 'Universal QR Service'

    @api.model
    def _get_payload_types(self):
        return constants.QR_PAYLOAD_TYPES

    @api.model
    def _get_action_types(self):
        return constants.QR_ACTION_TYPES

    @api.model
    def _get_qr_sizes(self):
        return constants.QR_SIZES

    @api.model
    def _get_qr_colors(self):
        return constants.QR_COLORS

    @api.model
    def _get_ecc_levels(self):
        return constants.QR_ECC_LEVELS

    @api.model
    def _get_expiration_policies(self):
        return constants.QR_EXPIRATION

    @api.model
    def _get_default_settings(self):
        icp = self.env['ir.config_parameter'].sudo()
        return {
            'qr_size': icp.get_param('rn_universal_qr.default_size', constants.DEFAULT_QR_SIZE),
            'qr_color': icp.get_param('rn_universal_qr.default_color', constants.DEFAULT_QR_COLOR),
            'custom_color': icp.get_param('rn_universal_qr.custom_color', '#000000'),
            'ecc_level': icp.get_param('rn_universal_qr.ecc_level', constants.DEFAULT_ECC_LEVEL),
            'use_logo': icp.get_param('rn_universal_qr.use_logo', 'False') == 'True',
            'payload_type': icp.get_param('rn_universal_qr.payload_type', constants.DEFAULT_PAYLOAD_TYPE),
            'action_type': icp.get_param('rn_universal_qr.action_type', constants.DEFAULT_ACTION_TYPE),
            'expiration_policy': icp.get_param('rn_universal_qr.expiration_policy', 'never'),
            'enable_statistics': icp.get_param('rn_universal_qr.enable_statistics', 'True') == 'True',
            'enable_public_url': icp.get_param('rn_universal_qr.enable_public_url', 'True') == 'True',
        }

    @api.model
    def _get_model_config(self, res_model, company_id=None):
        domain = [
            ('model_name', '=', res_model),
            ('active', '=', True),
        ]
        if company_id:
            domain += ['|', ('company_id', '=', company_id), ('company_id', '=', False)]
        return self.env['rn.qr.model.config'].sudo().search(domain, limit=1)

    @api.model
    def get_or_create_qr(self, res_model, res_id, values=None):
        target = self.env[res_model].browse(res_id)
        if not target.exists():
            raise UserError(_('Record not found for QR generation.'))

        existing = self.env['rn.qr.record'].search([
            ('res_model', '=', res_model),
            ('res_id', '=', res_id),
            ('active', '=', True),
        ], limit=1, order='id desc')

        defaults = self._get_default_settings()
        config = self._get_model_config(res_model, target._get_qr_company_id() if hasattr(target, '_get_qr_company_id') else self.env.company.id)
        if config:
            defaults.update(config.get_values_for_record())
        if values:
            defaults.update(values)

        company_id = defaults.get('company_id') or (
            target.company_id.id if 'company_id' in target._fields and target.company_id else self.env.company.id
        )

        if existing:
            write_vals = {k: v for k, v in defaults.items() if k in self.env['rn.qr.record']._fields and v is not False}
            if write_vals:
                existing.write(write_vals)
            if not existing.qr_image:
                existing.qr_image = self.render_qr_image(existing)
            return existing

        expiration_policy = defaults.get('expiration_policy', 'never')
        expires_on = self._compute_expiration(expiration_policy)

        qr_vals = {
            'res_model': res_model,
            'res_id': res_id,
            'company_id': company_id,
            'payload_type': defaults.get('payload_type', constants.DEFAULT_PAYLOAD_TYPE),
            'action_type': defaults.get('action_type', constants.DEFAULT_ACTION_TYPE),
            'qr_size': defaults.get('qr_size', constants.DEFAULT_QR_SIZE),
            'qr_color': defaults.get('qr_color', constants.DEFAULT_QR_COLOR),
            'custom_color': defaults.get('custom_color', '#000000'),
            'ecc_level': defaults.get('ecc_level', constants.DEFAULT_ECC_LEVEL),
            'use_logo': defaults.get('use_logo', False),
            'template_id': defaults.get('template_id'),
            'expiration_policy': expiration_policy,
            'expires_on': expires_on,
            'enable_report': defaults.get('enable_report', False),
        }
        qr_record = self.env['rn.qr.record'].create(qr_vals)
        qr_record.qr_image = self.render_qr_image(qr_record)
        return qr_record

    @api.model
    def regenerate_qr(self, res_model, res_id):
        qr = self.env['rn.qr.record'].search([
            ('res_model', '=', res_model),
            ('res_id', '=', res_id),
            ('active', '=', True),
        ], limit=1, order='id desc')
        if not qr:
            return self.get_or_create_qr(res_model, res_id)
        return self.regenerate_qr_record(qr)

    @api.model
    def regenerate_qr_record(self, qr_record):
        qr_record.write({
            'token': qr_record._default_token(),
            'scan_count': 0,
            'first_scan': False,
            'last_scan': False,
            'expires_on': self._compute_expiration(qr_record.expiration_policy),
        })
        qr_record.qr_image = self.render_qr_image(qr_record)
        return qr_record

    @api.model
    def _compute_expiration(self, policy):
        if not policy or policy == 'never':
            return False
        days = int(policy)
        return fields.Datetime.now() + timedelta(days=days)

    @api.model
    def build_payload(self, qr_record):
        target = self.env[qr_record.res_model].browse(qr_record.res_id)
        payload_type = qr_record.payload_type
        if payload_type == 'record_url':
            return qr_record.qr_url or ''
        if payload_type == 'internal_url':
            if not target.exists():
                return qr_record.qr_url or ''
            return '/web#id=%s&model=%s&view_type=form' % (qr_record.res_id, qr_record.res_model)
        if payload_type == 'public_url':
            if hasattr(target, 'access_token') and target.access_token:
                return '%s/my/%s/%s?access_token=%s' % (
                    self.env['ir.config_parameter'].sudo().get_param('web.base.url', '').rstrip('/'),
                    qr_record.res_model.replace('.', '/'),
                    qr_record.res_id,
                    target.access_token,
                )
            return qr_record.qr_url or ''
        if payload_type == 'record_name':
            return target.display_name if target.exists() else ''
        if payload_type == 'barcode':
            if target.exists() and 'barcode' in target._fields and target.barcode:
                return target.barcode
            return target.display_name if target.exists() else ''
        if payload_type == 'custom_text':
            return qr_record.custom_text or ''
        return qr_record.qr_url or ''

    @api.model
    def render_qr_image(self, qr_record):
        payload = self.build_payload(qr_record)
        if not payload:
            raise UserError(_('QR payload is empty.'))

        size = int(qr_record.qr_size or constants.DEFAULT_QR_SIZE)
        ecc = getattr(qrcode.constants, 'ERROR_CORRECT_%s' % (qr_record.ecc_level or 'M'))
        fill_color = self._resolve_color(qr_record)

        qr = qrcode.QRCode(
            version=None,
            error_correction=ecc,
            box_size=max(1, size // 25),
            border=2,
        )
        qr.add_data(payload)
        qr.make(fit=True)
        img = qr.make_image(fill_color=fill_color, back_color='white').convert('RGB')

        if qr_record.use_logo:
            img = self._apply_logo(img)

        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        return base64.b64encode(buffer.getvalue())

    @api.model
    def _resolve_color(self, qr_record):
        if qr_record.qr_color == 'company':
            company = qr_record.company_id or self.env.company
            return company.email_secondary_color or company.primary_color or '#000000'
        if qr_record.qr_color == 'custom':
            return qr_record.custom_color or '#000000'
        return constants.QR_COLOR_HEX.get(qr_record.qr_color, '#000000')

    @api.model
    def _apply_logo(self, img):
        company = self.env.company
        logo = company.logo
        if not logo:
            return img
        try:
            logo_data = base64.b64decode(logo)
            logo_img = Image.open(io.BytesIO(logo_data)).convert('RGBA')
        except Exception:
            _logger.warning('Could not load company logo for QR overlay.')
            return img

        qr_width, qr_height = img.size
        logo_max = int(min(qr_width, qr_height) * 0.22)
        logo_img.thumbnail((logo_max, logo_max), Image.Resampling.LANCZOS)

        pos = (
            (qr_width - logo_img.size[0]) // 2,
            (qr_height - logo_img.size[1]) // 2,
        )
        img.paste(logo_img, pos, logo_img if logo_img.mode == 'RGBA' else None)
        return img

    @api.model
    def render_qr_svg(self, qr_record):
        payload = self.build_payload(qr_record)
        size = int(qr_record.qr_size or constants.DEFAULT_QR_SIZE)
        ecc = getattr(qrcode.constants, 'ERROR_CORRECT_%s' % (qr_record.ecc_level or 'M'))
        fill_color = self._resolve_color(qr_record)
        qr = qrcode.QRCode(version=None, error_correction=ecc, box_size=8, border=2)
        qr.add_data(payload)
        qr.make(fit=True)
        try:
            import qrcode.image.svg
            factory = qrcode.image.svg.SvgPathImage
            svg_img = qr.make_image(image_factory=factory, fill_color=fill_color, back_color='white')
            stream = io.BytesIO()
            svg_img.save(stream)
            return stream.getvalue().decode('utf-8')
        except Exception as exc:
            raise UserError(_('SVG export failed: %s') % exc) from exc

    @api.model
    def download_png(self, res_model, res_id):
        qr = self.get_or_create_qr(res_model, res_id)
        if not qr.qr_image:
            qr.qr_image = self.render_qr_image(qr)
        filename = 'qr_%s_%s.png' % (res_model.replace('.', '_'), res_id)
        return {
            'type': 'ir.actions.act_url',
            'url': '/web/content/rn.qr.record/%s/qr_image/%s?download=true' % (qr.id, filename),
            'target': 'self',
        }

    @api.model
    def download_svg(self, res_model, res_id):
        qr = self.get_or_create_qr(res_model, res_id)
        svg_content = self.render_qr_svg(qr)
        attachment = self.env['ir.attachment'].create({
            'name': 'qr_%s_%s.svg' % (res_model.replace('.', '_'), res_id),
            'type': 'binary',
            'datas': base64.b64encode(svg_content.encode('utf-8')),
            'mimetype': 'image/svg+xml',
            'res_model': 'rn.qr.record',
            'res_id': qr.id,
        })
        return {
            'type': 'ir.actions.act_url',
            'url': '/web/content/%s?download=true' % attachment.id,
            'target': 'self',
        }

    @api.model
    def bulk_generate_zip(self, res_model, res_ids, values=None):
        if not res_ids:
            raise UserError(_('Select at least one record.'))
        import zipfile

        buffer = io.BytesIO()
        with zipfile.ZipFile(buffer, 'w', zipfile.ZIP_DEFLATED) as zf:
            for res_id in res_ids:
                qr = self.get_or_create_qr(res_model, res_id, values)
                if not qr.qr_image:
                    qr.qr_image = self.render_qr_image(qr)
                png_data = base64.b64decode(qr.qr_image)
                filename = 'qr_%s_%s.png' % (res_model.replace('.', '_'), res_id)
                zf.writestr(filename, png_data)
        zip_b64 = base64.b64encode(buffer.getvalue())
        attachment = self.env['ir.attachment'].create({
            'name': 'qr_bulk_%s.zip' % res_model.replace('.', '_'),
            'type': 'binary',
            'datas': zip_b64,
            'mimetype': 'application/zip',
        })
        return {
            'type': 'ir.actions.act_url',
            'url': '/web/content/%s?download=true' % attachment.id,
            'target': 'self',
        }

    @api.model
    def resolve_scan_action(self, qr_record, request=None):
        if qr_record.is_expired():
            raise UserError(_('This QR code has expired.'))

        target = self.env[qr_record.res_model].browse(qr_record.res_id)
        action_type = qr_record.action_type

        if action_type == 'open_record':
            if not target.exists():
                raise UserError(_('Linked record is no longer available.'))
            return {
                'type': 'ir.actions.act_url',
                'url': '/web#id=%s&model=%s&view_type=form' % (qr_record.res_id, qr_record.res_model),
                'target': 'self',
            }
        if action_type == 'portal_page':
            return {
                'type': 'ir.actions.act_url',
                'url': qr_record.custom_url or qr_record.qr_url,
                'target': 'self',
            }
        if action_type == 'download_pdf':
            report = self._find_report_for_model(qr_record.res_model)
            if report and target.exists():
                return {
                    'type': 'ir.actions.act_url',
                    'url': '/report/pdf/%s/%s' % (report.report_name, qr_record.res_id),
                    'target': 'new',
                }
            raise UserError(_('No PDF report configured for this model.'))
        if action_type == 'custom_url':
            if not qr_record.custom_url:
                raise UserError(_('Custom URL is not configured.'))
            return {
                'type': 'ir.actions.act_url',
                'url': qr_record.custom_url,
                'target': 'self',
            }
        if action_type == 'server_action' and qr_record.server_action_id:
            return qr_record.server_action_id.with_context(
                active_id=qr_record.res_id,
                active_ids=[qr_record.res_id],
                active_model=qr_record.res_model,
            ).run()
        return {
            'type': 'ir.actions.act_url',
            'url': qr_record.qr_url,
            'target': 'self',
        }

    @api.model
    def _find_report_for_model(self, res_model):
        return self.env['ir.actions.report'].search([
            ('model', '=', res_model),
            ('report_type', '=', 'qweb-pdf'),
        ], limit=1)
