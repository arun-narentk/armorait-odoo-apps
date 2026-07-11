/** @odoo-module **/

import { KanbanRenderer } from "@web/views/kanban/kanban_renderer";
import { patch } from "@web/core/utils/patch";
import { fetchColorTags } from "./color_tags_service";

patch(KanbanRenderer.prototype, {
    async onWillRenderRecords() {
        await super.onWillRenderRecords?.();
        const model = this.props.list?.resModel;
        const records = this.props.list?.records || [];
        if (!model || !records.length) {
            return;
        }
        const ids = records.map((record) => record.resId).filter(Boolean);
        if (!ids.length) {
            return;
        }
        const tags = await fetchColorTags(model, ids);
        for (const record of records) {
            const tag = tags[String(record.resId)] || {};
            if (tag.css_class) {
                record.rnColorTagClass = tag.css_class;
            }
            if (tag.label) {
                record.rnColorTagLabel = tag.label;
            }
            if (tag.emoji) {
                record.rnColorTagEmoji = tag.emoji;
            }
        }
    },

    getCardClass(record) {
        const classes = super.getCardClass(record);
        if (record.rnColorTagClass) {
            return `${classes} ${record.rnColorTagClass}`.trim();
        }
        return classes;
    },
});
