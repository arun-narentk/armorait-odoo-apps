# ARMORA Apps Store Capture Index

Per-module checklists live in `marketplace/CAPTURE_CHECKLIST.md` after you run `python build_marketplace.py --init`.

| Module | App name | Branch | Dashboard | Reports | Mobile | Checklist |
|--------|----------|--------|-----------|---------|--------|-----------|
| `rn_ai_document_generator` | AI Document Automation | feature/rn-ai-document-generator | yes | yes | no | `rn_ai_document_generator/marketplace/CAPTURE_CHECKLIST.md` |
| `rn_ai_employee` | AI Chatbot | feature/ai-employee | yes | no | yes | `rn_ai_employee/marketplace/CAPTURE_CHECKLIST.md` |
| `rn_bi_sales_dashboard` | Sales Dashboard | feature/rn-bi-sales-dashboard | yes | yes | yes | `rn_bi_sales_dashboard/marketplace/CAPTURE_CHECKLIST.md` |
| `rn_booking_platform` | Appointment Booking | feature/rn-booking-platform | yes | no | yes | `rn_booking_platform/marketplace/CAPTURE_CHECKLIST.md` |
| `rn_crm_ultimate_pro` | CRM Enhancements | feature/rn-crm-ultimate-pro | yes | yes | yes | `rn_crm_ultimate_pro/marketplace/CAPTURE_CHECKLIST.md` |
| `rn_dashboard_core` | Dashboard Core | feature/rn-dashboard-core | yes | no | yes | `rn_dashboard_core/marketplace/CAPTURE_CHECKLIST.md` |
| `rn_fleet_gps` | Fleet GPS Tracking | feature/rn-fleet-gps | yes | yes | yes | `rn_fleet_gps/marketplace/CAPTURE_CHECKLIST.md` |
| `rn_hms_core` | Hospital ERP | feature/rn-hms-core | yes | yes | yes | `rn_hms_core/marketplace/CAPTURE_CHECKLIST.md` |
| `rn_hr_attendance_face` | Attendance Face Recognition | feature/rn-hr-attendance-face | yes | no | yes | `rn_hr_attendance_face/marketplace/CAPTURE_CHECKLIST.md` |
| `rn_hr_resume_ai_parser` | Resume AI Parser | feature/ai-employee | no | no | yes | `rn_hr_resume_ai_parser/marketplace/CAPTURE_CHECKLIST.md` |
| `rn_hrms_core` | HRMS Core | feature/rn-hrms-core | yes | no | yes | `rn_hrms_core/marketplace/CAPTURE_CHECKLIST.md` |
| `rn_inventory_forecast` | Inventory Forecast | feature/rn-inventory-forecast | yes | yes | yes | `rn_inventory_forecast/marketplace/CAPTURE_CHECKLIST.md` |
| `rn_l10n_in_gst_pro` | GST Reports | feature/rn-l10n-in-gst-pro | yes | yes | no | `rn_l10n_in_gst_pro/marketplace/CAPTURE_CHECKLIST.md` |
| `rn_payroll_portal_pro` | Payroll Portal | local | yes | no | yes | `rn_payroll_portal_pro/marketplace/CAPTURE_CHECKLIST.md` |
| `rn_profit_guard` | Profit Guard | local | yes | yes | no | `rn_profit_guard/marketplace/CAPTURE_CHECKLIST.md` |
| `rn_rental_core` | Rental Management | feature/rn-rental-core | yes | yes | yes | `rn_rental_core/marketplace/CAPTURE_CHECKLIST.md` |
| `rn_restaurant_core` | Restaurant Management | feature/rn-restaurant-core | yes | no | yes | `rn_restaurant_core/marketplace/CAPTURE_CHECKLIST.md` |
| `rn_smart_credit_shield` | Credit Control | local | yes | yes | yes | `rn_smart_credit_shield/marketplace/CAPTURE_CHECKLIST.md` |
| `rn_theme_base` | Website Theme Framework | feature/theme-base | no | no | yes | `rn_theme_base/marketplace/CAPTURE_CHECKLIST.md` |
| `rn_whatsapp_connector` | WhatsApp Automation | feature/rn-whatsapp-connector | yes | yes | yes | `rn_whatsapp_connector/marketplace/CAPTURE_CHECKLIST.md` |
| `rn_whatsapp_integration` | WhatsApp Integration | local | no | no | yes | `rn_whatsapp_integration/marketplace/CAPTURE_CHECKLIST.md` |

## Workflow

1. Install module on capture DB `armora_apps_capture`
2. Run `python tools/apps_marketplace/capture_real_assets.py` or record manually
3. Copy PNG/GIF files into `marketplace/screenshots/` and `marketplace/gifs/`
4. Run `python build_marketplace.py <module> --zip`
5. Upload ZIP from `apps_store_zips/`

