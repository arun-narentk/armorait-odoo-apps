# Sale Order Customer Previous Price

See what you charged this customer last time, directly while creating a quotation.

## Problem

Salespeople often quote without checking the last price paid by that customer. That leads to inconsistent pricing and awkward customer conversations.

## Solution

On each sale order line, show:

- **Previous Customer Price**: latest confirmed unit price for the same product
- **Previous Customer Order**: the source order (openable)
- **Previous Order Date**
- **Difference vs Previous Price** and **Difference %**

The current **Unit Price is never changed automatically**.

## How previous price is chosen

1. Same commercial partner as the order customer
2. Same product
3. Same company
4. Confirmed orders only (`sale`; legacy `done` included if present)
5. Cancelled and draft/sent quotations ignored
6. Current order excluded
7. Newest `date_order` wins
8. Exact latest line `price_unit` (no average/min/max)

If the previous order used another currency, the amount is converted into the current order currency using Odoo rates on the previous order date.

## Configuration

No settings. Install and use.

## Compatibility

- Odoo 19 Community
- Depends on `sale_management`

## License

OPL-1

## Support

ARMORA IT Technologies  
https://www.armorait.com  
info@armorait.com
