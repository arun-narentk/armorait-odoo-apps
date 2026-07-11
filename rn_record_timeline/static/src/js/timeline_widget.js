/** @odoo-module **/

import { registry } from "@web/core/registry";
import { standardFieldProps } from "@web/views/fields/standard_field_props";
import { Component, useState, onWillStart } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";
import { _t } from "@web/core/l10n/translation";

export class RnRecordTimelineWidget extends Component {
    static template = "rn_record_timeline.TimelineWidget";
    static props = {
        ...standardFieldProps,
    };

    setup() {
        this.orm = useService("orm");
        this.action = useService("action");
        this.state = useState({
            loading: true,
            events: [],
            filter: "all",
            offset: 0,
            hasMore: false,
            total: 0,
            recordName: "",
        });
        onWillStart(() => this.loadEvents(false));
    }

    get resModel() {
        return this.props.record.resModel;
    }

    get resId() {
        return this.props.record.resId;
    }

    async loadEvents(append = false) {
        if (!this.resId) {
            this.state.loading = false;
            return;
        }
        this.state.loading = true;
        const offset = append ? this.state.offset : 0;
        const filterCategory = this.state.filter === "all" ? false : this.state.filter;
        const payload = await this.orm.call(
            this.resModel,
            "timeline_widget_data",
            [[this.resId]],
            {
                filter_category: filterCategory,
                limit: 50,
                offset,
            }
        );
        const events = append ? [...this.state.events, ...payload.events] : payload.events;
        Object.assign(this.state, {
            loading: false,
            events,
            offset: offset + payload.events.length,
            hasMore: payload.has_more,
            total: payload.total,
            recordName: payload.record?.name || "",
        });
    }

    async onFilterChange(ev) {
        this.state.filter = ev.target.value;
        this.state.offset = 0;
        await this.loadEvents(false);
    }

    async loadMore() {
        if (!this.state.hasMore || this.state.loading) {
            return;
        }
        await this.loadEvents(true);
    }

    async openRelated(event) {
        if (!event.related_model || !event.related_res_id) {
            return;
        }
        await this.action.doAction({
            type: "ir.actions.act_window",
            name: event.name,
            res_model: event.related_model,
            view_mode: "form",
            res_id: event.related_res_id,
            target: "current",
        });
    }

    async exportPdf() {
        const action = await this.orm.call(
            this.resModel,
            "action_export_timeline_pdf",
            [[this.resId]]
        );
        if (action) {
            await this.action.doAction(action);
        }
    }

    formatDate(value) {
        if (!value) {
            return "";
        }
        return value.replace("T", " ").slice(0, 16);
    }
}

registry.category("fields").add("rn_record_timeline", {
    component: RnRecordTimelineWidget,
    supportedTypes: ["integer"],
});
