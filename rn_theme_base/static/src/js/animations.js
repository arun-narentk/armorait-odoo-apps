/** @odoo-module **/

import { Interaction } from "@web/public/interaction";
import { registry } from "@web/core/registry";

const REVEAL_SELECTOR = ".tb-reveal, .tb-reveal-left, .tb-reveal-right";

function animateCounter(el) {
    const target = parseInt(el.dataset.target || el.textContent, 10);
    if (Number.isNaN(target)) {
        return;
    }
    const duration = parseInt(el.dataset.duration || "1500", 10);
    const suffix = el.dataset.suffix || "";
    const start = performance.now();
    const step = (now) => {
        const progress = Math.min((now - start) / duration, 1);
        const value = Math.floor(progress * target);
        el.textContent = `${value}${suffix}`;
        if (progress < 1) {
            requestAnimationFrame(step);
        } else {
            el.textContent = `${target}${suffix}`;
        }
    };
    requestAnimationFrame(step);
}

export class TbAnimations extends Interaction {
    static selector = "body";

    setup() {
        if (document.body.dataset.tbAnimations === "0") {
            return;
        }
        this.observer = new IntersectionObserver(
            (entries) => {
                for (const entry of entries) {
                    if (entry.isIntersecting) {
                        entry.target.classList.add("tb-revealed");
                        if (entry.target.classList.contains("tb-counter-value") || entry.target.classList.contains("tb-counter")) {
                            animateCounter(entry.target);
                        }
                        this.observer.unobserve(entry.target);
                    }
                }
            },
            { rootMargin: "0px 0px -8% 0px", threshold: 0.1 }
        );
        for (const el of document.querySelectorAll(REVEAL_SELECTOR)) {
            this.observer.observe(el);
        }
        for (const el of document.querySelectorAll(".tb-counter-value[data-target], .tb-counter[data-target]")) {
            if (!el.classList.contains("tb-reveal")) {
                this.observer.observe(el);
            }
        }
    }

    destroy() {
        this.observer?.disconnect();
        super.destroy();
    }
}

export class TbStickyHeader extends Interaction {
    static selector = "body.tb-header-sticky";

    setup() {
        this.header = document.querySelector("header");
        if (!this.header) {
            return;
        }
        this.onScroll = () => {
            this.header.classList.toggle("tb-header-scrolled", window.scrollY > 8);
        };
        window.addEventListener("scroll", this.onScroll, { passive: true });
        this.onScroll();
    }

    destroy() {
        window.removeEventListener("scroll", this.onScroll);
        super.destroy();
    }
}

registry.category("public.interactions").add("rn_theme_base.animations", TbAnimations);
registry.category("public.interactions").add("rn_theme_base.sticky_header", TbStickyHeader);
