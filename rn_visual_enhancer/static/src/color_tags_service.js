/** @odoo-module **/

import { registry } from "@web/core/registry";
import { rpc } from "@web/core/network/rpc";

const tagCache = new Map();

export async function fetchColorTags(model, recordIds) {
    if (!model || !recordIds?.length) {
        return {};
    }
    const key = `${model}:${recordIds.join(",")}`;
    if (tagCache.has(key)) {
        return tagCache.get(key);
    }
    const tags = await rpc("/rn_visual_enhancer/tags", { model, record_ids: recordIds });
    tagCache.set(key, tags);
    return tags;
}

export function clearColorTagCache() {
    tagCache.clear();
}

registry.category("services").add("rn_color_tags", {
    start() {
        return { fetchColorTags, clearColorTagCache };
    },
});
