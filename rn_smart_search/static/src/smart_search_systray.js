/** @odoo-module **/

import { Component, useState, onWillStart } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { Dropdown } from "@web/core/dropdown/dropdown";
import { useService } from "@web/core/utils/hooks";

export class RnSmartSearchSystray extends Component {
    static template = "rn_smart_search.Systray";
    static components = { Dropdown };
    static props = {};

    setup() {
        this.orm = useService("orm");
        this.action = useService("action");
        this.state = useState({
            loading: true,
            recentViews: [],
        });
        onWillStart(() => this.refresh());
    }

    async refresh() {
        this.state.loading = true;
        const data = await this.orm.call("rn.smart.search.service", "get_workspace_data", []);
        this.state.loading = false;
        this.state.recentViews = data.recent_views || [];
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

    async openWorkspace() {
        await this.action.doAction("rn_smart_search.action_rn_smart_search_workspace");
    }
}

registry.category("systray").add(
    "rn_smart_search.Systray",
    { Component: RnSmartSearchSystray },
    { sequence: 85 }
);
