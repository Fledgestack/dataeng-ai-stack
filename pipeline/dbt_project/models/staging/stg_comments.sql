select
    id           as comment_id,
    post_id,
    lower(email) as commenter_email,
    length(body) as body_length
from {{ source('raw', 'comments') }}
