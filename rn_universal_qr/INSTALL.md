# Installation

1. Place `rn_universal_qr` inside your addons path.
2. Install Python dependencies:
   - `pip install qrcode Pillow`
3. Update app list from Odoo Apps.
4. Install **Universal QR Generator**.
5. Configure defaults in Settings under Universal QR.

# Installation

1. Copy `rn_universal_qr` into your Odoo addons path.
2. Install Python dependencies:
   - `pip install qrcode Pillow`
3. Update apps list.
4. Install the module **Universal QR**.
5. Open Settings and configure defaults in the Universal QR block.
# Installation

## Requirements

- Odoo 19 Community
- Python 3.10+ (3.12 recommended)
- PostgreSQL
- Python packages: `qrcode`, `Pillow`

## Steps

1. Add `armora/` to your `addons_path`.
2. Update apps list.
3. Install **Universal QR Generator**.
4. Assign security groups to users.
5. Optional: enable extra models under **Universal QR > Configuration > Models**.

## Post-install

- Confirm `web.base.url` is correct so QR URLs resolve properly.
- Review **Settings > QR Generator** defaults before rollout.

## Support

info@armorait.com
