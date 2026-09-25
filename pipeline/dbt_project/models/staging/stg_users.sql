select
    id              as user_id,
    name            as user_name,
    username,
    lower(email)    as email,
    company__name   as company_name
from {{ source('raw', 'users') }}
