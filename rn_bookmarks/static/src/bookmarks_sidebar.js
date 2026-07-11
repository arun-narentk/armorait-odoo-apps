/** @odoo-module **/

import { Component, useState, onWillStart } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { Dropdown } from "@web/core/dropdown/dropdown";
import { useService } from "@web/core/utils/hooks";
import { debounce } from "@web/core/utils/timing";
import { clearBookmarkStateCache, reorderBookmarkIds } from "./bookmark_helpers";

export class RnBookmarksSidebar extends Component {
    static template = "rn_bookmarks.Sidebar";
    static components = { Dropdown };
    static props = {};

    setup() {
        this.orm = useService("orm");
        this.action = useService("action");
        this.state = useState({
            loading: true,
            search: "",
            pinned: [],
            favorites: [],
            recent: [],
            folders: [],
            unfiled: [],
            stats: { total: 0, pinned: 0, folders: 0, favorites: 0 },
            dragId: null,
            dragOverId: null,
        });
        this.debouncedRefresh = debounce(this.refresh.bind(this), 300);
        onWillStart(() => this.refresh());
    }

    async refresh() {
        this.state.loading = true;
        const data = await this.orm.call("rn.bookmark.service", "get_sidebar_data", [
            this.state.search || null,
            200,
        ]);
        this.state.pinned = data.pinned || [];
        this.state.favorites = data.favorites || [];
        this.state.recent = data.recent || [];
        this.state.folders = data.folders || [];
        this.state.unfiled = data.unfiled || [];
        this.state.stats = data.stats || this.state.stats;
        this.state.loading = false;
    }

    async onSearch() {
        await this.debouncedRefresh();
    }

    async openBookmark(bookmarkId) {
        const bookmark = await this.orm.read("rn.bookmark", [bookmarkId], ["id"]);
        if (!bookmark.length) {
            return;
        }
        const clientAction = await this.orm.call("rn.bookmark", "action_open_bookmark", [bookmarkId]);
        if (clientAction) {
            await this.action.doAction(clientAction);
        }
        await this.refresh();
    }

    async openDashboard() {
        await this.action.doAction("rn_bookmarks.action_rn_bookmark_dashboard");
    }

    onDragStart(item, ev) {
        this.state.dragId = item.id;
        ev.dataTransfer.effectAllowed = "move";
    }

    onDragOver(item, ev) {
        ev.preventDefault();
        this.state.dragOverId = item.id;
    }

    onDragLeave() {
        this.state.dragOverId = null;
    }

    async onDrop(sectionItems, targetItem, ev) {
        ev.preventDefault();
        const fromId = this.state.dragId;
        const toId = targetItem?.id;
        this.state.dragId = null;
        this.state.dragOverId = null;
        if (!fromId || !toId || fromId === toId) {
            return;
        }
        const ids = sectionItems.map((item) => item.id);
        const fromIndex = ids.indexOf(fromId);
        const toIndex = ids.indexOf(toId);
        if (fromIndex < 0 || toIndex < 0) {
            return;
        }
        ids.splice(fromIndex, 1);
        ids.splice(toIndex, 0, fromId);
        clearBookmarkStateCache();
        await reorderBookmarkIds(this.orm, ids);
        await this.refresh();
    }

    bookmarkItemClass(item) {
        const classes = ["o_rn_bookmark_item", "d-flex", "align-items-center", "gap-2", "py-1"];
        if (this.state.dragOverId === item.id) {
            classes.push("o_rn_bookmark_drag_over");
        }
        return classes.join(" ");
    }

    colorClass(color) {
        const mapping = {
            green: "text-success",
            blue: "text-primary",
            orange: "text-warning",
            red: "text-danger",
            purple: "text-info",
            teal: "text-info",
            gray: "text-muted",
        };
        return mapping[color] || "text-warning";
    }
}

registry.category("systray").add(
    "rn_bookmarks.Sidebar",
    { Component: RnBookmarksSidebar },
    { sequence: 82 }
);
