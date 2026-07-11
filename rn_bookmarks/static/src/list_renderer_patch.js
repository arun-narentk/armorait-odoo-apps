/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import { ListRenderer } from "@web/views/list/list_renderer";
import {
    clearBookmarkStateCache,
    fetchBookmarkStates,
    toggleRecordBookmark,
} from "./bookmark_helpers";

patch(ListRenderer.prototype, {
    get showBookmarkColumn() {
        const list = this.props.list;
        if (!list || list.isGrouped || !list.resModel) {
            return false;
        }
        return (list.records || []).some((record) => record.resId);
    },

    async onWillRenderRecords() {
        await super.onWillRenderRecords?.();
        const model = this.props.list?.resModel;
        const records = this.props.list?.records || [];
        const ids = records.map((record) => record.resId).filter(Boolean);
        if (!model || !ids.length) {
            return;
        }
        const states = await fetchBookmarkStates(model, ids);
        for (const record of records) {
            record.rnBookmarked = Boolean(states[String(record.resId)]);
        }
    },

    async onRnBookmarkStarClick(record, ev) {
        if (!record.resId) {
            return;
        }
        const icon = ev?.currentTarget?.querySelector?.(".o_rn_bookmark_star_icon") || ev?.currentTarget;
        icon?.classList?.add("o_rn_bookmark_star_pop");
        window.setTimeout(() => icon?.classList?.remove("o_rn_bookmark_star_pop"), 450);
        clearBookmarkStateCache();
        const state = await toggleRecordBookmark(
            this.env.services.orm,
            this.env.services.notification,
            this.props.list.resModel,
            record.resId
        );
        record.rnBookmarked = state.bookmarked;
    },
});
