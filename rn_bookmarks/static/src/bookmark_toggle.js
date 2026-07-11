/** @odoo-module **/

import { registry } from "@web/core/registry";
import { standardWidgetProps } from "@web/views/widgets/standard_widget_props";
import { useService } from "@web/core/utils/hooks";
import { Component, useState, onWillStart, useEffect } from "@odoo/owl";

export class RnBookmarkToggleWidget extends Component {
    static template = "rn_bookmarks.BookmarkToggle";
    static props = {
        ...standardWidgetProps,
    };

    setup() {
        this.orm = useService("orm");
        this.notification = useService("notification");
        this.state = useState({
            bookmarked: false,
            bookmarkId: false,
            loading: false,
        });
        onWillStart(() => this.refresh());
        useEffect(
            () => {
                if (this.resId) {
                    this.refresh();
                }
            },
            () => [this.props.record.resId]
        );
    }

    get resModel() {
        return this.props.record.resModel;
    }

    get resId() {
        return this.props.record.resId;
    }

    async refresh() {
        if (!this.resId) {
            this.state.bookmarked = false;
            this.state.bookmarkId = false;
            return;
        }
        const data = await this.orm.call(
            "rn.bookmark.service",
            "get_current_context_bookmark_state",
            [this.resModel, this.resId]
        );
        this.state.bookmarked = data.bookmarked;
        this.state.bookmarkId = data.bookmark_id;
    }

    async onToggle() {
        if (!this.resId || this.state.loading) {
            return;
        }
        this.state.loading = true;
        const wasBookmarked = this.state.bookmarked;
        try {
            await this.orm.call(this.resModel, "action_toggle_rn_bookmark", [[this.resId]]);
            await this.refresh();
            await this.props.record.load();
            this.notification.add(
                !wasBookmarked ? "Bookmark saved." : "Bookmark removed.",
                { type: "success" }
            );
        } catch (error) {
            this.notification.add("Could not update bookmark.", { type: "danger" });
        } finally {
            this.state.loading = false;
        }
    }
}

export const rnBookmarkToggle = {
    component: RnBookmarkToggleWidget,
};

registry.category("view_widgets").add("rn_bookmark_toggle", rnBookmarkToggle);
