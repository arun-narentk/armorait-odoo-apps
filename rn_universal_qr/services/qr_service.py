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
        company = self.env.company
        if 'company_id' in business_record._fields and business_record.company_id:
            company = business_record.company_id
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
