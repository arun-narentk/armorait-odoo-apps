/** @odoo-module **/

import { registry } from "@web/core/registry";
import { rpc } from "@web/core/network/rpc";

export async function fetchFieldDiffs(model, resId, limit = 50) {
    return rpc("/rn_field_diff/diffs", { model, res_id: resId, limit });
}

export async function fetchFieldDiffSummary(model, resId) {
    return rpc("/rn_field_diff/summary", { model, res_id: resId });
}

registry.category("services").add("rn_field_diff", {
    start() {
        return { fetchFieldDiffs, fetchFieldDiffSummary };
    },
});
