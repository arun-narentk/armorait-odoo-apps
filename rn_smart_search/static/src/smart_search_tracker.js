/** @odoo-module **/

import { registry } from "@web/core/registry";
import { standardWidgetProps } from "@web/views/widgets/standard_widget_props";
import { useService } from "@web/core/utils/hooks";
import { Component, onWillStart, useEffect } from "@odoo/owl";

export class RnSmartSearchTrackerWidget extends Component {
    static template = "rn_smart_search.Tracker";
    static props = {
        ...standardWidgetProps,
    };

    setup() {
        this.orm = useService("orm");
        onWillStart(() => this.trackView());
        useEffect(
            () => {
                this.trackView();
            },
            () => [this.props.record.resId]
        );
    }

    async trackView() {
        const resId = this.props.record.resId;
        const resModel = this.props.record.resModel;
        if (!resId || !resModel) {
            return;
        }
        try {
            await this.orm.call(resModel, "smart_search_track_view", [[resId]]);
        } catch (_error) {
            // Tracking should never block form rendering.
        }
    }
}

export const rnSmartSearchTracker = {
    component: RnSmartSearchTrackerWidget,
};

registry.category("view_widgets").add("rn_smart_search_tracker", rnSmartSearchTracker);
