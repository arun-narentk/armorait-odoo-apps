# ARMORA Hospital ERP Core

Affordable hospital and clinic management for Odoo 19 Community.

## Overview

`rn_hms_core` is the shared foundation of ARMORA Hospital ERP for small hospitals, clinics, and diagnostic centers (roughly 5-100 beds). It provides patients, doctors, departments, wards, beds, appointments, SaaS edition tracking, OWL dashboard, and APIs used by companion HMS modules.

## Business Problem

Small healthcare facilities need an affordable, easy-to-deploy system. Large hospital stacks are too complex. ARMORA Hospital ERP targets practical front-office, OPD, and bed occupancy first, then layers pharmacy, lab, IPD, and insurance.

## Suite Architecture

```
rn_hms_core
├── rn_hms_patient / rn_hms_doctor / rn_hms_appointment (planned polish modules)
├── rn_hms_billing (Accounting)
├── rn_hms_pharmacy (Inventory)
├── rn_hms_lab
├── rn_hms_ipd
├── rn_hms_insurance
├── rn_hms_patient_portal
└── rn_hms_dashboard / rn_hms_ai
```

Design rule: do not re-implement HR, Inventory, Purchase, Accounting, or Payroll inside HMS. Integrate with standard Odoo Community apps and optional ARMORA Booking / HRMS platforms.

## Phase 1 Features

- Departments, doctors, patients
- Appointment calendar + tokens
- Wards, beds, occupancy allocation
- Register / quick appointment / admit wizards
- OWL hospital dashboard
- Subscription editions (Starter, Standard, Professional, SaaS)
- Security, crons, docs, Apps assets

## Installation

1. Install Contacts, Calendar, HR, Portal.
2. Update Apps List.
3. Install **ARMORA Hospital ERP Core**.
4. Configure departments, doctors, wards, and hospital settings.

## Marketplace Pricing

Professional foundation priced at **99.00 USD**. Bundle editions later (Starter / Standard / Professional / SaaS).

## Support

ARMORA IT Technologies  
Website: https://www.armorait.com  
Support: info@armorait.com

## License

OPL-1

## Credits

(c) ARMORA IT Technologies
