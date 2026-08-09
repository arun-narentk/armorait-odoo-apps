# Architecture

Controller stays thin and delegates selection to `ai.biz.promotion.service`.

```
Website /ai-biz
    -> AiBizPromotionController
        -> ai.biz.promotion.service.get_active_promotion()
            -> ai.biz.promotion + ai.biz.benefit
                -> QWeb template + frontend SCSS
```

ARMORA IT Technologies | https://www.armorait.com | info@armorait.com
