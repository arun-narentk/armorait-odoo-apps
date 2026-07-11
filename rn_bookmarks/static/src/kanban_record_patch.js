/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import { KanbanRecord } from "@web/views/kanban/kanban_record";
import { KanbanRenderer } from "@web/views/kanban/kanban_renderer";
import { useEffect } from "@odoo/owl";
import {
    clearBookmarkStateCache,
    fetchBookmarkStates,
    toggleRecordBookmark,
} from "./bookmark_helpers";

patch(KanbanRenderer.prototype, {
    setup() {
        super.setup(...arguments);
        useEffect(
            () => {
                this.loadRnBookmarkStates();
            },
            () => [
                this.props.list?.resModel,
                (this.props.list?.records || []).map((record) => record.resId).join(","),
            ]
        );
    },

    async loadRnBookmarkStates() {
        const list = this.props.list;
        const records = list?.records || [];
        const ids = records.map((record) => record.resId).filter(Boolean);
        if (!list?.resModel || !ids.length) {
            return;
        }
        const states = await fetchBookmarkStates(list.resModel, ids);
        for (const record of records) {
            record.rnBookmarked = Boolean(states[String(record.resId)]);
        }
    },
});

patch(KanbanRecord.prototype, {
    get rnBookmarked() {
        return Boolean(this.props.record.rnBookmarked);
    },

    async onRnKanbanBookmarkClick(ev) {
        ev.preventDefault();
        ev.stopPropagation();
        const record = this.props.record;
        if (!record.resId) {
            return;
        }
        ev.currentTarget?.querySelector?.(".o_rn_bookmark_star_icon")?.classList?.add("o_rn_bookmark_star_pop");
        window.setTimeout(() => {
            ev.currentTarget?.querySelector?.(".o_rn_bookmark_star_icon")?.classList?.remove("o_rn_bookmark_star_pop");
        }, 450);
        clearBookmarkStateCache();
        const state = await toggleRecordBookmark(
            this.env.services.orm,
            this.env.services.notification,
            record.resModel,
            record.resId
        );
        record.rnBookmarked = state.bookmarked;
    },
});
