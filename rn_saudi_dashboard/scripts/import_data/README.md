# Saudi Arabia Demo Accounting Data

Import-ready data for an Odoo 19 accounting demo (currency: **SAR**, VAT: **15%**).

## Files

| File | Model | Records |
|------|-------|---------|
| `customers.csv` | `res.partner` | 5 customers (VAT registered) |
| `vendors.csv` | `res.partner` | 5 vendors (VAT registered) |
| `products.csv` | `product.product` | 5 service products |
| `customer_invoices.csv` | `account.move` | 13 customer invoices |
| `vendor_bills.csv` | `account.move` | 7 vendor bills |

## Two ways to load

### Option A — One-shot script (recommended for demos)

Loads everything, posts the invoices/bills, registers payments and marks
overdue receivables. It also removes any previous demo data first.

```bash
odoo-bin shell -d <db> --no-http < ../load_saudi_demo_data.py
```

### Option B — Manual CSV import (UI)

Import in this order so relations resolve by name:

1. `customers.csv` and `vendors.csv` → **Contacts → Import**
2. `products.csv` → **Accounting → Vendors/Customers → Products → Import**
3. `customer_invoices.csv` → **Accounting → Customers → Invoices → Import**
4. `vendor_bills.csv` → **Accounting → Vendors → Bills → Import**

Notes:
- Invoices/bills import as **Draft**; select all and use **Post** to confirm.
- Blank leading columns on a row mean "another line of the previous invoice".
- The `15%` tax column matches the localization sale/purchase VAT tax. If your
  database has more than one tax named `15%`, set the correct one after import.

## Example transactions

- Customer invoice: **ERP Consulting Service** 10,000 + 15% VAT = **11,500 SAR**
- Vendor bill: **Office Equipment Purchase** 5,000 + 15% VAT = **5,750 SAR**
