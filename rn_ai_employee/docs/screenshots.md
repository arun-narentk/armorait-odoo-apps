# Screenshots and Demo Assets

Marketplace assets live in `static/description/`.

## Regenerate demo assets

```bash
python3 armora/rn_ai_employee/scripts/generate_demo_assets.py
```

This builds Odoo-style screenshots and workflow GIFs for the Apps Store page.

## PNG screenshots

| File | Purpose |
|------|---------|
| `banner.png` | Apps Store cover card (1200x600, navy gradient + indigo/cyan palette) |
| `banner_small.png` | Listing thumbnail (360x180) |
| `icon.png` | Module icon |
| `overview.png` | Systray copilot conversation |
| `settings.png` | Platform settings toggles |
| `tools.png` | Skill registry list |
| `list.png` | Conversation history |
| `dashboard.png` | Executive morning briefing |
| `report.png` | Audit log |
| `mobile.png` | Mobile systray panel |
| `form.png` | Audit detail (alias) |
| `wizard.png` | Confirmation flow (alias) |

## Animated GIFs

| File | Story |
|------|-------|
| `workflow.gif` | 6-step loop: Observe, Reason, Decide, Act, Explain, Audit |
| `hero.gif` | Copilot + settings overview |
| `dashboard.gif` | Executive briefing + copilot |
| `settings.gif` | Settings + skill registry |
| `reports.gif` | Audit log + skills |
| `mobile.gif` | Mobile workflow (first 3 steps) |

## Replace with live captures

When Odoo is running with the module installed, replace generated assets with real Playwright captures using `tools/apps_marketplace/capture_marketplace.py` on the `feature/chore-armora-product-builder` branch.

Capture: systray, chat form, settings, audit log, skill registry, morning briefing, mobile systray.
