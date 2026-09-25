---
title: User Engagement
---

Built from `dlt → DuckLake → dbt → Postgres`, orchestrated by Dagster. Every number on this page traces back to a versioned SQL file.

```sql totals
select
  count(*)                 as users,
  sum(posts)               as posts,
  sum(comments_received)   as comments
from analytics.user_engagement
```

<BigValue data={totals} value=users />
<BigValue data={totals} value=posts />
<BigValue data={totals} value=comments />

## Comments received by user

```sql by_user
select user_name, comments_received, posts
from analytics.user_engagement
order by comments_received desc
```

<BarChart data={by_user} x=user_name y=comments_received swapXY=true />

## Detail

<DataTable data={by_user} />
