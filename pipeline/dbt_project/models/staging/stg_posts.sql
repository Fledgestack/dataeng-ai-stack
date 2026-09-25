select
    id          as post_id,
    user_id,
    title,
    length(body) as body_length
from {{ source('raw', 'posts') }}
