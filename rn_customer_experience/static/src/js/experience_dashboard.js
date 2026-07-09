/** @odoo-module **/

import { registry } from "@web/core/registry";
import { Component, useState, onWillStart } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";

export class RnCustomerExperienceDashboard extends Component {
    static template = "rn_customer_experience.Dashboard";

    setup() {
        this.orm = useService("orm");
        this.state = useState({
            loading: true,
            data: {},
        });
        onWillStart(async () => {
            await this.reload();
        });
    }

    async reload() {
        this.state.loading = true;
        this.state.data = await this.orm.call(
            "rn.customer.experience.analytics.service",
            "get_admin_dashboard",
            []
        );
        this.state.loading = false;
    }
}

registry.category("actions").add("rn_customer_experience.dashboard", RnCustomerExperienceDashboard);
