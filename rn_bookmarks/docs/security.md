# Security (docs)

See [SECURITY.md](../SECURITY.md) for the full policy.

## Summary

- Private bookmarks per `user_id`
- Record rules on bookmark, folder, tag models
- JSON controllers require authenticated users
- Opening bookmarks respects target model ACLs

## Audit

`last_opened_at` and `open_count` support usage review per bookmark.

## Hardening

- No `sudo()` on open except timestamp write on own bookmark
- Validation on duplicate record bookmarks via Python constraint
