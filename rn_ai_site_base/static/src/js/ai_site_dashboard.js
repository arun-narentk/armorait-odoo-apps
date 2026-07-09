/** @odoo-module **/

import { registry } from "@web/core/registry";
import { Component, onWillStart, useState } from "@odoo/owl";
import { rpc } from "@web/core/network/rpc";

class AiSiteDashboard extends Component {
    static template = "rn_ai_site_base.AiSiteDashboard";

    setup() {
        this.state = useState({ cards: [], briefs: [] });
        onWillStart(async () => {
            const data = await rpc("/rn_ai_site_base/dashboard/data");
            const cards = data.cards || {};
            this.state.cards = [
                { key: "briefs", label: "Briefs", value: cards.briefs || 0 },
                { key: "sites", label: "Websites", value: cards.sites || 0 },
                { key: "published", label: "Published", value: cards.published || 0 },
                { key: "ready", label: "Ready", value: cards.ready || 0 },
                { key: "draft", label: "Draft Briefs", value: cards.draft_briefs || 0 },
                { key: "credits", label: "AI Credits", value: cards.ai_credits || 0 },
            ];
            this.state.briefs = data.recent_briefs || [];
        });
    }
}

registry.category("actions").add("rn_ai_site_dashboard", AiSiteDashboard);
