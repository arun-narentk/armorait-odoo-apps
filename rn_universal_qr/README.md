# Universal QR Generator

Universal QR Generator adds QR generation and scan tracking to all business records in Odoo 19 Community.

## Features

- Global mixin via `base` inheritance
- Secure token route `/rn/qr/<token>`
- Scan log with source, timestamp, and network info
- QR templates and model-level configuration
- Bulk ZIP generation wizard
- Label and A4 PDF reports
- Report QR blocks for sales, purchase, invoices, and delivery

## Dependencies

- Odoo 19 Community
- Python: `qrcode`, `Pillow`

## Support

- ARMORA IT Technologies
- https://www.armorait.com
- info@armorait.com

# Universal QR for Odoo 19

Universal QR adds QR generation to all business models through a global mixin inheritance on `base`.

## Key features

- QR fields and actions available on all records
- Public scan route with token resolution and scan logs
- QR registry, templates, and per-model configuration
- Bulk ZIP generation wizard
- Label and A4 PDF reports
- Report inheritance for Sale, Purchase, Invoice, and Delivery documents

## Dependencies

- Odoo 19 Community
- Python package `qrcode`
- Python package `Pillow`

## Support

- ARMORA IT Technologies
- Website: https://www.armorait.com
- Email: info@armorait.com
# Universal QR Generator

Generate secure, token-based QR codes for any Odoo 19 record. Print on reports and labels, track scans, and configure multiple QR actions without model-specific code.

## Business Problem

Most QR modules only cover one document type (invoice or sale order). Teams need one engine that works across sales, warehouse, CRM, HR, products, and custom models.

## Features

- Generic QR engine via `rn.qr.mixin` on all models
- Token URLs (`/rn/qr/<token>`) instead of exposing database IDs
- Payload options: secure URL, internal URL, public URL, record name, barcode, custom text
- Action options: open record, portal page, PDF download, custom URL, server action
- Size, color, logo overlay, and ECC level controls
- Expiration policies and regeneration
- Scan statistics with user, device, and IP logging
- Bulk ZIP export from list selections
- QR templates for warehouse, office, customer, and manufacturing
- Report blocks on quotation, invoice, purchase order, and delivery slip

## Installation

1. Install Python dependencies: `qrcode`, `Pillow` (included in standard Odoo requirements).
2. Install **Universal QR Generator** from Apps.
3. Assign **Universal QR / User** or **Manager** groups.
4. Open **Universal QR > Configuration > Models** to enable additional models.

## Configuration

Go to **Settings > QR Generator** for defaults: size, color, payload, action, statistics, and report options.

## Permissions

| Group | Access |
|-------|--------|
| User | Generate, download, and scan QR on allowed records |
| Manager | Templates, model config, scan logs, and full QR record management |

## Support

ARMORA IT Technologies | https://www.armorait.com | info@armorait.com

## License

OPL-1. Copyright ARMORA IT Technologies.
