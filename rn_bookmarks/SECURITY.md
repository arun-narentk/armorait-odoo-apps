# Security

## Access model

Bookmarks are **private per user**. Each user sees only their own bookmarks, folders, and tags.

## Groups

| Group | Technical name |
|-------|----------------|
| User | `rn_bookmarks.group_rn_bookmarks_user` |
| Manager | `rn_bookmarks.group_rn_bookmarks_manager` |

Managers inherit user rights. Root and admin are pre-assigned to Manager.

## Record rules

| Model | Rule |
|-------|------|
| `rn.bookmark` | `user_id = current user` |
| `rn.bookmark.folder` | `user_id = current user` + multi-company |
| `rn.bookmark.tag` | `user_id = current user` |

## Controllers

All `/rn/bookmark/*` JSON routes use `auth='user'`. No public bookmark data.

## Data isolation

- Bookmarks store `res_model` and `res_id` but opening still respects target model access rights.
- Service methods verify `bookmark.user_id` before open or move.

## Recommendations

- Do not grant bookmark manager to portal users.
- Use separate staging databases when testing shared-folder features in v2.

## Reporting issues

security@armorait.com or info@armorait.com
