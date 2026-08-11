# Product Last Sale Price

See what this customer last paid for a product, directly on the Sale Order line.

## Description

When a salesperson selects a customer and product, the module shows the effective unit price from that customer's most recent confirmed sale of the same product.

## Features

- Last Sale Price on each sale order line
- Latest confirmed sale only (not the highest price)
- Effective price after line discount
- Current order excluded from history
- Draft quotations and cancelled orders ignored
- Commercial partner matching
- Multi-company aware
- Multi-currency and UoM conversion
- Informational only (does not change Unit Price)

## Installation

1. Add the module to your addons path
2. Update the Apps list
3. Install **Product Last Sale Price**

## Configuration

No configuration. Works after install.

## Usage

1. Open or create a quotation
2. Select the customer
3. Add a product line
4. Read **Last Sale Price** next to Unit Price

## Example

Historical confirmed sales for ABC Industries / Product A:

| Order | Date | Unit Price |
| --- | --- | ---: |
| SO001 | 2026-01-10 | 100 |
| SO002 | 2026-03-15 | 125 |
| SO003 | 2026-05-20 | 110 |

New quotation today:

```text
Last Sale Price = 110
```

If a historical line had Unit Price 100 and Discount 10%, Last Sale Price = 90.

## Technical notes

- Extends `sale.order.line` with computed `last_sale_price`
- Batches historical order lookup to avoid N+1 searches
- Confirmed states: `sale` (and legacy `done` if present)
- Ordering: `date_order desc`, then `id desc`
- Depends on `sale_management`

## Supported Odoo version

Odoo 19 Community (this repository).

## License

LGPL-3

## Support

ARMORA IT Technologies  
https://www.armorait.com  
info@armorait.com
