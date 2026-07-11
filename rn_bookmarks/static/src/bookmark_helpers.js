/** @odoo-module **/

import { rpc } from "@web/core/network/rpc";

const stateCache = new Map();

export function clearBookmarkStateCache() {
    stateCache.clear();
}

export async function fetchBookmarkStates(model, recordIds) {
    if (!model || !recordIds?.length) {
        return {};
    }
    const key = `${model}:${recordIds.join(",")}`;
    if (stateCache.has(key)) {
        return stateCache.get(key);
    }
    const states = await rpc("/rn/bookmark/states", {
        res_model: model,
        res_ids: recordIds,
    });
    stateCache.set(key, states);
    return states;
}

export async function toggleRecordBookmark(orm, notification, model, recordId) {
    clearBookmarkStateCache();
    await orm.call(model, "action_toggle_rn_bookmark", [[recordId]]);
    const state = await orm.call("rn.bookmark.service", "get_current_context_bookmark_state", [
        model,
        recordId,
    ]);
    if (notification) {
        notification.add(state.bookmarked ? "Bookmark saved." : "Bookmark removed.", {
            type: "success",
        });
    }
    return state;
}

export async function reorderBookmarkIds(orm, bookmarkIds) {
    if (!bookmarkIds?.length) {
        return;
    }
    await orm.call("rn.bookmark.service", "reorder_bookmarks", [bookmarkIds]);
}
