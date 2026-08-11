/** @odoo-module **/

/**
 * Visualization registry placeholder.
 * Each chart renderer registers itself in later phases.
 */
export const visualizationRegistry = new Map();

export function registerVisualization(itemType, renderer) {
    visualizationRegistry.set(itemType, renderer);
}

export function getVisualization(itemType) {
    return visualizationRegistry.get(itemType) || null;
}
