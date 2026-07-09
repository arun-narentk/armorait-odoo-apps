/** @odoo-module **/

import { registry } from "@web/core/registry";
import { Component, useState, onWillStart } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";

export class RnWorkflowDesigner extends Component {
    static template = "rn_workflow_builder.Designer";

    setup() {
        this.orm = useService("orm");
        this.state = useState({
            loading: true,
            workflow: {},
            nodes: [],
        });
        onWillStart(async () => {
            const workflowId = this.props.action?.params?.workflow_id;
            if (workflowId) {
                await this.load(workflowId);
            } else {
                this.state.loading = false;
            }
        });
    }

    async load(workflowId) {
        this.state.loading = true;
        const data = await this.orm.call(
            "rn.workflow.engine",
            "get_designer_data",
            [workflowId]
        );
        this.state.workflow = data.workflow || {};
        this.state.nodes = data.nodes || [];
        this.state.loading = false;
    }
}

registry.category("actions").add("rn_workflow_builder.designer", RnWorkflowDesigner);
