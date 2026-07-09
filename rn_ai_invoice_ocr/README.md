# AI Invoice OCR

ARMORA IT Technologies commercial module for Odoo 19 Community.

Upload supplier invoices (PDF, JPG, PNG), extract fields with OCR, match vendors and products, detect duplicates, and create draft vendor bills after review.

## Phase 1 features

- Drag-and-drop invoice upload
- Text extraction and field parsing (vendor, GSTIN, invoice number, dates, amounts)
- Line item extraction with confidence scores
- India GST parsing (CGST, SGST, IGST, HSN hooks)
- Fuzzy vendor and product matching with learned mappings
- Duplicate invoice detection
- One-click draft vendor bill creation
- OCR credit tracking and subscription model hooks
- OWL dashboard with KPI cards

## Installation

1. Copy `rn_ai_invoice_ocr` into your Odoo addons path.
2. Update the apps list and install **AI Invoice OCR**.
3. Assign users to **OCR User** or **OCR Manager** groups.
4. Configure OCR settings under **AI Invoice OCR > Configuration**.

Optional: install `pypdf` or `PyPDF2` on the server for PDF text extraction.

## Usage

1. Open **AI Invoice OCR > Invoice Scans** and create a record with an attachment.
2. Click **Run OCR** to extract fields and line items.
3. Review confidence scores and fix vendor or product matches if needed.
4. Click **Create Vendor Bill** to generate a draft `in_invoice`.

## Permissions

| Group | Access |
|-------|--------|
| OCR User | Upload, extract, review, create bills |
| OCR Manager | Full access including settings and subscriptions |

## Support

- Website: https://www.armorait.com
- Email: info@armorait.com

## License

OPL-1. See LICENSE file.
