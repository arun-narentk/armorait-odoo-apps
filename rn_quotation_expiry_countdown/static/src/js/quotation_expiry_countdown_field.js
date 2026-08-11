/** @odoo-module **/

import { _t } from "@web/core/l10n/translation";
import { registry } from "@web/core/registry";
import { sprintf } from "@web/core/utils/strings";
import { standardFieldProps } from "@web/views/fields/standard_field_props";
import { Component, onMounted, onWillUnmount, useEffect, useState } from "@odoo/owl";

/**
 * Live quotation expiry countdown.
 * Recomputes from validity_date on the client every 60 seconds (no RPC).
 */
export class QuotationExpiryCountdownField extends Component {
    static template = "rn_quotation_expiry_countdown.QuotationExpiryCountdownField";
    static props = {
        ...standardFieldProps,
    };

    setup() {
        this.state = useState({
            text: "",
            urgency: "none",
            now: Date.now(),
        });
        this._interval = null;
        useEffect(
            () => {
                this._refresh();
            },
            () => [
                this.props.record.data.validity_date,
                this.props.record.data.state,
                this.state.now,
            ]
        );
        onMounted(() => {
            this._refresh();
            this._interval = setInterval(() => {
                this.state.now = Date.now();
            }, 60000);
        });
        onWillUnmount(() => {
            if (this._interval) {
                clearInterval(this._interval);
                this._interval = null;
            }
        });
    }

    get cssClass() {
        const map = {
            ok: "text-success fw-bold",
            warning: "text-warning fw-bold",
            expired: "text-danger fw-bold",
            none: "text-muted",
        };
        return map[this.state.urgency] || "text-muted";
    }

    _refresh() {
        const data = this.props.record.data;
        const orderState = data.state;
        const validity = data.validity_date;
        if (!["draft", "sent"].includes(orderState) || !validity) {
            this.state.text = "";
            this.state.urgency = "none";
            return;
        }
        const result = this._buildCountdown(validity);
        this.state.text = result.text;
        this.state.urgency = result.urgency;
    }

    /**
     * @param {string} validityDate YYYY-MM-DD
     */
    _buildCountdown(validityDate) {
        const warningHours = 24;
        const now = new Date(this.state.now);
        const today = new Date(now.getFullYear(), now.getMonth(), now.getDate());
        const [y, m, d] = validityDate.split("-").map((v) => parseInt(v, 10));
        const validity = new Date(y, m - 1, d);
        const dayMs = 24 * 60 * 60 * 1000;
        const dayDiff = Math.round((validity - today) / dayMs);

        if (dayDiff < 0) {
            const days = Math.abs(dayDiff);
            return {
                text:
                    days <= 1
                        ? _t("Expired 1 day ago")
                        : sprintf(_t("Expired %s days ago"), days),
                urgency: "expired",
            };
        }
        if (dayDiff === 0) {
            return { text: _t("Expires today"), urgency: "warning" };
        }

        const expiryEnd = new Date(y, m - 1, d, 23, 59, 59);
        const remainingMs = expiryEnd - now;
        if (remainingMs <= 0) {
            return { text: _t("Expires today"), urgency: "warning" };
        }
        const remainingHours = remainingMs / (60 * 60 * 1000);

        if (remainingHours < 1) {
            const minutes = Math.max(1, Math.floor(remainingMs / 60000));
            return {
                text:
                    minutes === 1
                        ? _t("Expires in 1 minute")
                        : sprintf(_t("Expires in %s minutes"), minutes),
                urgency: "warning",
            };
        }
        if (remainingHours < warningHours) {
            const hours = Math.max(1, Math.floor(remainingHours));
            return {
                text:
                    hours === 1
                        ? _t("Expires in 1 hour")
                        : sprintf(_t("Expires in %s hours"), hours),
                urgency: "warning",
            };
        }
        if (dayDiff <= 1) {
            return { text: _t("Expires in 1 day"), urgency: "ok" };
        }
        return {
            text: sprintf(_t("Expires in %s days"), dayDiff),
            urgency: "ok",
        };
    }
}

export const quotationExpiryCountdownField = {
    component: QuotationExpiryCountdownField,
    displayName: _t("Quotation Expiry Countdown"),
    supportedTypes: ["char"],
};

registry.category("fields").add("rn_quotation_expiry_countdown", quotationExpiryCountdownField);
