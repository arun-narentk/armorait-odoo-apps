/** @odoo-module **/

import { Component, useState, onWillStart } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { Dropdown } from "@web/core/dropdown/dropdown";
import { useService } from "@web/core/utils/hooks";
import { debounce } from "@web/core/utils/timing";

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
            folders: [],
            unfiled: [],
            stats: { total: 0, pinned: 0, folders: 0, favorites: 0 },
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
}

registry.category("systray").add(
    "rn_bookmarks.Sidebar",
    { Component: RnBookmarksSidebar },
    { sequence: 82 }
);
