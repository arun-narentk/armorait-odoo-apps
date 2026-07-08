/** @odoo-module **/

/**
 * Chart dataset helpers for Chart.js bindings (Phase 2+).
 * Phase 1 exposes normalized series only; canvas rendering comes next.
 */

export function formatMoney(value) {
    const num = Number(value || 0);
    return num.toLocaleString(undefined, { maximumFractionDigits: 2 });
}

export function normalizeChart(chart) {
    if (!chart) {
        return { type: "bar", labels: [], datasets: [] };
    }
    return {
        type: chart.type || "bar",
        labels: chart.labels || [],
        datasets: chart.datasets || [],
    };
}
