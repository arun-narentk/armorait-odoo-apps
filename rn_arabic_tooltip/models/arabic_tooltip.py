from odoo import api, models


class RnArabicTooltip(models.AbstractModel):
    _name = "rn.arabic.tooltip"
    _description = "Arabic Tooltip Translation Provider"

    # Conservative accounting fallback used when Odoo's own translation
    # catalog does not provide an Arabic term for a given English label.
    _AR_FALLBACK = {
        "Amount": "المبلغ",
        "Amount Due": "المبلغ المستحق",
        "Customer": "العميل",
        "Customer Invoice": "فاتورة العميل",
        "Customer Credit Note": "إشعار دائن للعميل",
        "Vendor Bill": "فاتورة المورد",
        "Vendor Credit Note": "إشعار دائن للمورد",
        "Date": "التاريخ",
        "Delivery Date": "تاريخ التسليم",
        "Draft": "مسودة",
        "Due Date": "تاريخ الاستحقاق",
        "Invoice Date": "تاريخ الفاتورة",
        "Invoice Lines": "بنود الفاتورة",
        "Invoiced": "المفوتر",
        "Journal Entry": "قيد اليومية",
        "Journal Items": "بنود القيد",
        "Label": "الوصف",
        "Payment": "الدفع",
        "Payment Status": "حالة الدفع",
        "Document Type": "نوع المستند",
        "Type": "النوع",
        "Posted": "مرحل",
        "Price": "السعر",
        "Quantity": "الكمية",
        "Reference": "المرجع",
        "Status": "الحالة",
        "Subtotal": "الإجمالي الفرعي",
        "Taxes": "الضرائب",
        "Terms and Conditions": "الشروط والأحكام",
        "Total": "الإجمالي",
        "Untaxed Amount": "المبلغ قبل الضريبة",
        "VAT Total Amount": "إجمالي ضريبة القيمة المضافة",
        "Vendor": "المورد",
        "Currency": "العملة",
        # Invoice status (payment_state) values
        "Not Paid": "غير مدفوع",
        "In Payment": "قيد الدفع",
        "Paid": "مدفوع",
        "Partially Paid": "مدفوع جزئيًا",
        "Reversed": "معكوس",
        "Cancelled": "ملغى",
    }

    @api.model
    def get_arabic_label_translations(self, labels):
        """Return Arabic translations for the given English UI labels.

        We first ask Odoo's standard translation engine in the active Arabic
        language; when a term is not translated by Odoo, we use a conservative
        accounting fallback dictionary.
        """
        # Prefer an installed (active) Arabic language so we read Odoo's own
        # standard translations; fall back to ar_001 for the gettext lookup.
        installed_ar = self.env["res.lang"].search(
            [("code", "=like", "ar%"), ("active", "=", True)], limit=1
        )
        lang = installed_ar.code or "ar_001"
        result = {}
        for label in labels or []:
            source = (label or "").strip()
            if not source:
                continue
            # 1) Standard value: Odoo's own translation in the Arabic language.
            translated = self.with_context(lang=lang).env._(source)
            # 2) Automatic fallback: accounting dictionary tailored for Saudi.
            if not translated or translated == source:
                translated = self._AR_FALLBACK.get(source)
            if translated and translated != source:
                result[source] = translated
        return result
