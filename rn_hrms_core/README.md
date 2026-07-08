# ARMORA HRMS Core

Modern HR & Payroll Platform for Small and Medium Businesses

## Overview

`rn_hrms_core` is the shared foundation of the ARMORA HRMS suite for Odoo 19 Community. It provides employee extensions, branches, designations, documents, announcements, a reusable approval engine, SaaS subscription metadata, notifications, OWL dashboard, and APIs used by companion modules.

## Business Problem

SMBs with 10-300 employees need a modern HR platform with self-service, payroll, attendance, and recruitment. Odoo Community provides a foundation; ARMORA HRMS fills the commercial gaps as a modular suite.

## Suite Architecture

```
rn_hrms_core
├── rn_hr_employee (planned)
├── rn_hr_attendance (planned)
├── rn_hr_leave (planned)
├── rn_hr_payroll (planned)
├── rn_hr_recruitment (planned)
├── rn_hr_performance (planned)
├── rn_hr_employee_portal (planned)
└── rn_hr_dashboard / integrations (planned)
```

## Phase 1 Features

- Branches, designations, skills
- Employee HRMS fields and documents
- Announcements
- Generic multi-level approval requests
- Onboarding wizard and employee codes
- Subscription / edition tracking (Starter, Professional, Enterprise, SaaS)
- OWL HR dashboard shell
- Security, crons, docs, Apps assets

## Installation

1. Install HR (`hr`) and Portal.
2. Update Apps List.
3. Install **ARMORA HRMS Core**.
4. Configure branches, designations, and HRMS settings.

## Marketplace Pricing

Suite foundation priced at **49.00 USD** (Starter edition positioning). Companion modules can be sold separately (Professional / Enterprise bundles later).

## Support

ARMORA IT Technologies  
Website: https://www.armorait.com  
Support: info@armorait.com

## License

OPL-1

## Credits

(c) ARMORA IT Technologies
