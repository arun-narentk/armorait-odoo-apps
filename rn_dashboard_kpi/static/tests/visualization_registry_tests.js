/** @odoo-module **/

import { beforeEach, describe, expect, test } from "@odoo/hoot";
import {
    getVisualization,
    registerVisualization,
    visualizationRegistry,
} from "@rn_dashboard_kpi/utils/visualization_registry";

describe("rn_dashboard_kpi visualization registry", () => {
    beforeEach(() => {
        visualizationRegistry.clear();
    });

    test("registers and resolves a visualization", () => {
        const stub = { render() {} };
        registerVisualization("tile", stub);
        expect(getVisualization("tile")).toBe(stub);
        expect(getVisualization("missing")).toBe(null);
    });
});
