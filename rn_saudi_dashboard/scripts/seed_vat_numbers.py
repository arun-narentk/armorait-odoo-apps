"""Seed Saudi VAT registration numbers on the company and demo customers.

Run with:
    odoo-bin shell -d rn --no-http < this_file.py

Saudi VAT numbers are 15 digits, starting and ending with 3. Adding them lets
the dashboard mark customer invoices as fully ZATCA-compliant.
"""

company = env.company

if not company.vat:
    company.vat = "300000000000003"
if company.country_id and company.country_id.code != "SA":
    sa = env.ref("base.sa")
    company.country_id = sa.id

vat_by_customer = {
    "Al Rajhi Trading Est.": "310111111100003",
    "Jeddah Industrial Co.": "310222222200003",
    "Riyadh Tech Solutions": "310333333300003",
    "Dammam Logistics LLC": "310444444400003",
    "Makkah Retail Group": "310555555500003",
}

updated = 0
for name, vat in vat_by_customer.items():
    partner = env["res.partner"].search([("name", "=", name)], limit=1)
    if partner and not partner.vat:
        partner.vat = vat
        if not partner.country_id:
            partner.country_id = env.ref("base.sa").id
        updated += 1

env.cr.commit()
print("=== VAT NUMBERS SEEDED ===")
print("Company VAT:", company.vat)
print("Customers updated:", updated)
