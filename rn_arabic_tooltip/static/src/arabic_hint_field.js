import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { user } from "@web/core/user";
import { _t } from "@web/core/l10n/translation";
import { standardFieldProps } from "@web/views/fields/standard_field_props";
import { Component, useState, useRef, onMounted, onWillUnmount } from "@odoo/owl";

/**
 * Field widget: shows the field value and, on hover, a custom Arabic tooltip.
 *
 * Usage in a view:
 *     <field name="state" widget="rn_arabic_hint"/>
 *
 * Behaviour:
 *  - Only active when the user's UI language is English (when the UI is
 *    already Arabic the value is shown natively, so no hint is needed).
 *  - The Arabic value comes from Odoo's standard translation (when the Arabic
 *    language is installed and the term is translated); otherwise it falls
 *    back to an automatic accounting translation dictionary on the server.
 *  - Both the field value AND its label show the Arabic hint on hover. The
 *    label lives in a separate cell rendered by Odoo, so we locate it on
 *    mount and attach the same tooltip to it.
 */
export class ArabicHintField extends Component {
    static template = "rn_arabic_tooltip.ArabicHintField";
    static props = { ...standardFieldProps };

    setup() {
        this.orm = useService("orm");
        this.root = useRef("root");
        this.state = useState({ en: "", ar: "", visible: false, x: 0, y: 0 });
        this._cache = {};
        // Active only when the system language is English.
        this.enabled = !(user.lang || "").toLowerCase().startsWith("ar");

        this._labelEl = null;
        this._onLabelEnter = (ev) => this.onLabelEnter(ev);
        this._onLabelLeave = () => this.onLeave();

        onMounted(() => this._bindLabel());
        onWillUnmount(() => this._unbindLabel());
    }

    get displayText() {
        const field = this.props.record.fields[this.props.name];
        const raw = this.props.record.data[this.props.name];
        if (raw === false || raw === null || raw === undefined || raw === "") {
            return "";
        }
        if (field.type === "selection") {
            const opt = (field.selection || []).find((o) => o[0] === raw);
            return opt ? opt[1] : String(raw);
        }
        if (field.type === "many2one") {
            return Array.isArray(raw) ? raw[1] || "" : String(raw);
        }
        return String(raw);
    }

    // --- Label binding ----------------------------------------------------
    // Odoo renders the field label in a separate cell, so we walk backwards
    // from this widget's cell to the nearest preceding label and attach the
    // same hover tooltip to it.
    _bindLabel() {
        if (!this.enabled || !this.root.el) {
            return;
        }
        const cell = this.root.el.closest(".o_cell") || this.root.el.closest(".o_field_widget");
        if (!cell) {
            return;
        }
        let prev = cell.previousElementSibling;
        let label = null;
        while (prev && !label) {
            label = prev.matches("label, .o_form_label")
                ? prev
                : prev.querySelector("label, .o_form_label");
            prev = prev.previousElementSibling;
        }
        if (!label) {
            return;
        }
        this._labelEl = label;
        label.classList.add("o_rn_ar_hint_label");
        label.addEventListener("mouseenter", this._onLabelEnter);
        label.addEventListener("mouseleave", this._onLabelLeave);
    }

    _unbindLabel() {
        if (this._labelEl) {
            this._labelEl.removeEventListener("mouseenter", this._onLabelEnter);
            this._labelEl.removeEventListener("mouseleave", this._onLabelLeave);
            this._labelEl = null;
        }
    }

    // --- Hover handlers ---------------------------------------------------
    onLabelEnter() {
        if (!this._labelEl) {
            return;
        }
        // Labels may carry a trailing colon, help marker (?) or required (*).
        const text = (this._labelEl.textContent || "")
            .replace(/\s+/g, " ")
            .replace(/\s*[:：?*]+\s*$/, "")
            .trim();
        this._showTip(text, this._labelEl.getBoundingClientRect());
    }

    onHover(ev) {
        if (!this.enabled) {
            return;
        }
        this._showTip(this.displayText.trim(), ev.currentTarget.getBoundingClientRect());
    }

    async _showTip(text, rect) {
        if (!this.enabled || !text) {
            return;
        }
        this.state.en = text;
        this.state.x = Math.round(rect.left + rect.width / 2);
        this.state.y = Math.round(rect.top);
        this.state.visible = true;

        if (this._cache[text] !== undefined) {
            this.state.ar = this._cache[text];
            return;
        }
        this.state.ar = "";
        try {
            const res = await this.orm.call(
                "rn.arabic.tooltip",
                "get_arabic_label_translations",
                [[text]]
            );
            const ar = res[text] || "";
            this._cache[text] = ar;
            // Guard against a fast mouse-out before the RPC resolved.
            if (this.state.visible && this.state.en === text) {
                this.state.ar = ar;
            }
        } catch {
            this._cache[text] = "";
        }
    }

    onLeave() {
        this.state.visible = false;
    }
}

export const arabicHintField = {
    component: ArabicHintField,
    displayName: _t("Arabic Hint"),
    supportedTypes: ["char", "text", "selection", "many2one"],
};

registry.category("fields").add("rn_arabic_hint", arabicHintField);
