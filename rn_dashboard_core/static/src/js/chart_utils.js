/** @odoo-module **/

export function formatPercent(value) {
    return `${Number(value || 0).toFixed(1)}%`;
}

export function formatNumber(value) {
    return Number(value || 0).toLocaleString(undefined, { maximumFractionDigits: 2 });
}
