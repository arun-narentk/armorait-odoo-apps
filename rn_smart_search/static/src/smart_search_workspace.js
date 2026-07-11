/** @odoo-module **/

import { registry } from "@web/core/registry";
import { Component, useState, onWillStart } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";

export class RnSmartSearchWorkspace extends Component {
    static template = "rn_smart_search.Workspace";

    setup() {
        this.orm = useService("orm");
        this.action = useService("action");
        this.state = useState({
            loading: true,
            favorites: [],
            recent_views: [],
            recent_searches: [],
        });
        onWillStart(() => this.refresh());
    }

    async refresh() {
        this.state.loading = true;
        const data = await this.orm.call("rn.smart.search.service", "get_workspace_data", []);
        Object.assign(this.state, {
            loading: false,
            favorites: data.favorites || [],
            recent_views: data.recent_views || [],
            recent_searches: data.recent_searches || [],
        });
    }

    async openItem(historyId) {
        const clientAction = await this.orm.call(
            "rn.smart.search.service",
            "open_history_record",
            [historyId]
        );
        if (clientAction) {
            await this.action.doAction(clientAction);
        }
        await this.refresh();
    }

    async toggleFavorite(historyId) {
        await this.orm.call("rn.smart.search.service", "toggle_favorite", [historyId]);
        await this.refresh();
    }
}

registry.category("actions").add("rn_smart_search.workspace", RnSmartSearchWorkspace);
