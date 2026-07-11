/** @odoo-module **/

import { Component, onWillStart, useState } from "@odoo/owl";
import { Dialog } from "@web/core/dialog/dialog";
import { fetchFieldDiffs, fetchFieldDiffSummary } from "./field_diff_service";

export class DiffViewerDialog extends Component {
    static template = "rn_field_diff.DiffViewerDialog";
    static components = { Dialog };
    static props = {
        close: Function,
        model: String,
        resId: Number,
        title: { type: String, optional: true },
    };

    setup() {
        this.state = useState({ diffs: [], summary: {}, loading: true });
        onWillStart(async () => {
            const [diffs, summary] = await Promise.all([
                fetchFieldDiffs(this.props.model, this.props.resId),
                fetchFieldDiffSummary(this.props.model, this.props.resId),
            ]);
            this.state.diffs = diffs;
            this.state.summary = summary;
            this.state.loading = false;
        });
    }
}
