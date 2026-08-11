# Architecture

```
OWL client action
  -> rn.kpi.dashboard (+ items, filters, bookmarks)
      -> rn.kpi.dashboard.data.service
          -> ORM search_count / read_group (user rights)
```

Models hold configuration. Aggregation logic lives in the service layer.

ARMORA IT Technologies | https://www.armorait.com | info@armorait.com
