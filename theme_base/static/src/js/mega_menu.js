/** @odoo-module **/

import { Interaction } from "@web/public/interaction";
import { registry } from "@web/core/registry";

/**
 * Keyboard-accessible mega menu: arrow keys, Escape, focus trap basics.
 */
export class TbMegaMenu extends Interaction {
    static selector = ".o_mega_menu_toggle";

    setup() {
        this.el.setAttribute("aria-haspopup", "true");
        this.el.setAttribute("aria-expanded", "false");
        this.menuEl = this.el.closest(".nav-item")?.querySelector(".o_mega_menu");
        if (!this.menuEl) {
            return;
        }
        this.menuEl.classList.add("tb-mega-menu");
        this.menuItems = () =>
            [...this.menuEl.querySelectorAll("a, button")].filter((n) => !n.disabled);
        this.onKeydown = this.onKeydown.bind(this);
        this.el.addEventListener("keydown", this.onKeydown);
        this.menuEl.addEventListener("keydown", this.onKeydown);
    }

    onKeydown(ev) {
        const items = this.menuItems();
        if (!items.length) {
            return;
        }
        const idx = items.indexOf(document.activeElement);
        switch (ev.key) {
            case "ArrowDown":
                ev.preventDefault();
                items[(idx + 1) % items.length]?.focus();
                break;
            case "ArrowUp":
                ev.preventDefault();
                items[(idx - 1 + items.length) % items.length]?.focus();
                break;
            case "Home":
                ev.preventDefault();
                items[0]?.focus();
                break;
            case "End":
                ev.preventDefault();
                items[items.length - 1]?.focus();
                break;
            case "Escape":
                this.el.focus();
                break;
            default:
                break;
        }
    }

    destroy() {
        this.el.removeEventListener("keydown", this.onKeydown);
        this.menuEl?.removeEventListener("keydown", this.onKeydown);
        super.destroy();
    }
}

registry.category("public.interactions").add("theme_base.mega_menu", TbMegaMenu);
