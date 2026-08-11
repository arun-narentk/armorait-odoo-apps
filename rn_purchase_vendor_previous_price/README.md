# Purchase Vendor Previous Price

See what you paid this vendor last time, directly on Purchase Order lines.

## What it does

On each purchase order line, the module shows:

- **Previous Vendor Price**: latest confirmed unit price for the same product and vendor
- **Previous Vendor Price Date**: when that previous purchase was confirmed
- **Previous Vendor Order**: openable link to that PO

The current **Unit Price is never changed automatically**.

## Installation

1. Add the module to your addons path.
2. Update the Apps list.
3. Install **Purchase Vendor Previous Price**.

Depends on: `purchase`

## How previous price is calculated

1. Same commercial partner as the PO vendor
2. Same product
3. Same company
4. Confirmed POs only (`purchase`; legacy `done` included if present)
5. Draft / RFQ / sent / to approve / cancelled ignored
6. Current PO excluded
7. Newest confirmation date (`date_approve`, then `date_order`) wins
8. Exact latest line `price_unit` (no average/min/max)

If no previous purchase exists, the field is `0.0`.

## Currency behavior

If the previous PO used another currency, the amount is converted into the current PO currency using Odoo `res.currency._convert()` on the previous confirmation/order date.

## UoM behavior

If the previous line used a different UoM, the price is converted with standard
`uom.uom._compute_price()` (Odoo 19 relative-factor UoM model).

## Known limitations

- Only the latest confirmed purchase is shown (not a full price history).
- Odoo 19 has no separate `done` purchase state; confirmed orders are `purchase`.
- Odoo 19 UoM no longer uses categories; conversion relies on relative UoM factors.
- No settings page by design.

## Compatibility

Odoo 19 Community

## License

OPL-1

## Support

ARMORA IT Technologies  
https://www.armorait.com  
info@armorait.com
