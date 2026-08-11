# Product Last Purchase Price

See what you paid for a product the last time you bought it, on the product and on purchase order lines.

## Purpose

Buyers need a fast answer to: **"What did we pay for this product the last time we bought it?"**

This module shows that price on the product form/list and compares it to the current unit price on each purchase order line.

## Features

- Last Purchase Price, Date, Vendor, and Order on the product
- Previous purchase price on purchase order lines
- Price difference and difference %
- Informational warning when the price increased (does not block confirmation)
- Vendor-specific previous price, with fallback to any vendor
- Company-aware stored values on product variants
- Optional list column on products

## How last purchase is chosen

1. Confirmed purchase orders only (`purchase`; legacy `done` included if present)
2. Same company
3. Exact product variant
4. Latest `date_approve` (or `date_order`), then higher purchase order id, then line id
5. Cancelled and draft orders ignored

On a purchase order line:

1. Prefer the latest previous purchase from the **same vendor** (commercial partner)
2. If none, use the latest previous purchase from **any vendor**
3. The current order is excluded

## Installation

1. Add the module to your addons path
2. Update the Apps list
3. Install **Product Last Purchase Price**

No configuration menus.

## Usage

1. Confirm a purchase order for a product
2. Open the product: check the Last Purchase Price section
3. Create a new RFQ for the same product: see Last Purchase Price next to Unit Price
4. Compare Difference / Difference % when the vendor quote changed

## Dependencies

- `purchase` (includes `product`)

## Compatibility

- Odoo 19 Community

## License

OPL-1

## Support

ARMORA IT Technologies  
https://www.armorait.com  
info@armorait.com
