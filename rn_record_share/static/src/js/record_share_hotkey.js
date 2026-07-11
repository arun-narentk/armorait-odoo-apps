/** @odoo-module **/

import { registry } from "@web/core/registry";

const recordShareHotkeyService = {
    dependencies: ["hotkey", "orm", "action", "notification"],
    start(env, { hotkey, orm, action, notification }) {
        hotkey.add("control+shift+c", async () => {
            const actionService = env.services.action;
            const controller = actionService.currentController;
            if (!controller) {
                return;
            }
            const context = controller.action?.context || {};
            const model = controller.props?.resModel || context.res_model || context.active_model;
            const recordId = controller.props?.resId || context.res_id || context.active_id;
            if (!model || !recordId) {
                return;
            }
            try {
                const result = await orm.call(model, "action_copy_record_link", [[recordId]]);
                if (result) {
                    await action.doAction(result);
                }
            } catch (error) {
                notification.add("Copy link is not available on this screen.", {
                    type: "warning",
                });
            }
        });
    },
};

registry.category("services").add("rn_record_share_hotkey", recordShareHotkeyService);
