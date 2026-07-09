# Manufacturing MES

ARMORA IT Technologies shop-floor Manufacturing Execution System for Odoo 19 Community.

ERP plans production. MES executes it on the factory floor with real-time visibility.

## Business problem

Factories struggle between planning and production: which machine, which operator, why downtime, how much scrap, is quality OK. Standard MRP plans orders but does not run the shop floor.

## Phase 1 features

- Shop floor tablet UI (OWL kiosk)
- Work order start, pause, resume, complete
- Operator sessions and production events
- Scrap and reject capture
- Barcode scan logging (WO, product, operator, machine)
- Quality checklists and inspections
- Downtime reasons and events
- OEE snapshots (availability, performance, quality)
- Machine device registry and IoT reading hooks
- Plant manager dashboard and AI production insights

## Installation

1. Install **Manufacturing** (`mrp`), **HR**, **Inventory**, and **Barcodes**.
2. Install **Manufacturing MES**.
3. Assign **Shop Floor Operator**, **Production Supervisor**, or **MES Manager** groups.

## Usage

- **Manufacturing MES > Shop Floor Tablet** for operator execution
- **Manufacturing MES > Plant Dashboard** for live KPIs
- Configure terminals, checklists, and downtime reasons under Configuration

## Companion modules

- `rn_mrp_intelligence`: executive factory KPIs and command center (analytics layer)
- Future: IoT gateway connector, scheduling board, predictive maintenance AI

## Support

- https://www.armorait.com
- info@armorait.com

## License

OPL-1
