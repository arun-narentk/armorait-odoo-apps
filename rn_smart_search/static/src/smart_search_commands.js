/** @odoo-module **/

import { _t } from "@web/core/l10n/translation";
import { registry } from "@web/core/registry";
import { DefaultCommandItem } from "@web/core/commands/command_palette";

const commandCategoryRegistry = registry.category("command_categories");
commandCategoryRegistry.add("smart_search", { namespace: "default" }, { sequence: 5 });

const commandSetupRegistry = registry.category("command_setup");
commandSetupRegistry.add("default", {
    placeholder: _t("Search for a command..."),
}, { force: false });

const commandProviderRegistry = registry.category("command_provider");
commandProviderRegistry.add("rn_smart_search", {
    namespace: "default",
    async provide(env, options = {}) {
        const orm = env.services.orm;
        const actionService = env.services.action;
        const searchValue = options.searchValue || "";
        const items = await orm.call("rn.smart.search.service", "get_command_items", [searchValue]);
        return items.map((item) => ({
            Component: DefaultCommandItem,
            category: "smart_search",
            name: item.subtitle ? `${item.name} (${item.subtitle})` : item.name,
            action() {
                return orm.call("rn.smart.search.service", "open_history_record", [item.id]).then((action) => {
                    if (action) {
                        actionService.doAction(action);
                    }
                });
            },
        }));
    },
});
