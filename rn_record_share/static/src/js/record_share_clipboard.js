/** @odoo-module **/

import { _t } from "@web/core/l10n/translation";
import { registry } from "@web/core/registry";

async function copyClipboardAction(env, action) {
    const text = action.params?.text || "";
    const message = action.params?.message || _t("Copied to clipboard");
    try {
        await navigator.clipboard.writeText(text);
        env.services.notification.add(message, { type: "success" });
    } catch (error) {
        env.services.notification.add(_t("Could not copy to clipboard"), { type: "danger" });
    }
}

registry.category("actions").add("rn_record_share.copy_clipboard", copyClipboardAction);
