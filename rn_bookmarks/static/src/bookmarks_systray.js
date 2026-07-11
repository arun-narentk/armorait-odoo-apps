/** @odoo-module **/

import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";

const bookmarkHotkeyService = {
    dependencies: ["hotkey", "orm", "notification", "action"],
    start(env, { hotkey, orm, notification }) {
        hotkey.add("control+b", async () => {
            const actionService = env.services.action;
            const controller = actionService.currentController;
            if (!controller || controller.action.type !== "ir.actions.act_window") {
                return;
            }
            const { resModel, resId } = controller.action.context || {};
            const model = controller.props?.resModel || resModel;
            const recordId = controller.props?.resId || resId;
            if (!model || !recordId) {
                return;
            }
            try {
                await orm.call(model, "action_toggle_rn_bookmark", [[recordId]]);
                notification.add("Bookmark updated.", { type: "success" });
            } catch (error) {
                notification.add("Could not bookmark this record.", { type: "warning" });
            }
        });
    },
};

registry.category("services").add("rn_bookmark_hotkey", bookmarkHotkeyService);
