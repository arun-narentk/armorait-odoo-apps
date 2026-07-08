# Developer Guide

Register a custom trigger:

```python
env['rn.whatsapp.automation.service'].register_trigger('my_event', 'My Event')
env['rn.whatsapp.automation.service'].run_trigger('custom', records)
```

Add a provider by inheriting `rn.whatsapp.provider.base` and registering it in `PROVIDER_REGISTRY`.

ARMORA IT Technologies | https://www.armorait.com
