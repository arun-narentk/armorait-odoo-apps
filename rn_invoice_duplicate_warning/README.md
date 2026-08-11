# Invoice Duplicate Number Warning

Prevent accidental duplicate vendor invoices in Odoo 19.

## Problem

The same supplier invoice can be entered twice. That creates duplicate payables, messy reconciliation, and payment risk.

## Solution

Before a vendor bill is posted, the module checks whether another vendor bill already uses the same **Bill Reference** (`account.move.ref`) for the **same vendor** and **same company**.

## Features

- Duplicate vendor invoice detection on posting
- Same vendor (commercial partner) validation
- Multi-company support
- Warning mode (default)
- Blocking mode (optional)
- Case-insensitive reference matching (configurable)
- Trimmed whitespace matching
- Draft and posted duplicate detection
- Lightweight Accounting settings
- No extra menus or dashboards

## Scope

| Document | Behavior |
|---|---|
| Vendor bill (`in_invoice`) | Checked |
| Vendor credit note (`in_refund`) | Not checked as a bill duplicate |
| Customer invoice / credit note | Not affected |

Commercial partner is used so contacts under the same vendor cannot bypass the check.

## Configuration

Go to **Accounting → Configuration → Settings → Vendor Bills → Duplicate Invoice Warning**.

1. **Enable Duplicate Invoice Number Warning** (default: on)
2. **Block Duplicate Vendor Invoice** (default: off)
3. **Case-Insensitive Invoice Numbers** (default: on)

## Usage

1. Create a vendor bill and set **Bill Reference** to the supplier invoice number.
2. Click **Post**.
3. If a duplicate exists:
   - **Warning mode:** Cancel, open the existing bill, or Continue Anyway.
   - **Block mode:** Close and fix the reference before posting.

## Examples

Same vendor, same company, `INV-1001` then `inv-1001` → duplicate (case-insensitive on).

Same number, different vendors → not a duplicate.

Same number, different companies → not a duplicate.

Empty Bill Reference → no warning.

## Compatibility

Odoo 19 Community

Depends on: `account`

## License

LGPL-3

## Support

ARMORA IT Technologies  
https://www.armorait.com  
info@armorait.com
