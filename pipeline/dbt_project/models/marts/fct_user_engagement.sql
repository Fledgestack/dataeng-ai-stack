with posts as (
    select user_id, count(*) as posts, avg(body_length) as avg_post_length
    from {{ ref('stg_posts') }}
    group by 1
),
comments as (
    select p.user_id, count(c.comment_id) as comments_received
    from {{ ref('stg_posts') }} p
    left join {{ ref('stg_comments') }} c using (post_id)
    group by 1
)
select
    u.user_id,
    u.user_name,
    u.company_name,
    coalesce(p.posts, 0)                    as posts,
    coalesce(c.comments_received, 0)        as comments_received,
    round(coalesce(p.avg_post_length, 0), 1) as avg_post_length,
    round(coalesce(c.comments_received, 0) / nullif(p.posts, 0), 2) as comments_per_post
from {{ ref('stg_users') }} u
left join posts p using (user_id)
left join comments c using (user_id)
