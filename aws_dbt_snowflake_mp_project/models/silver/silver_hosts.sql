{{
  config(
    materialized = 'incremental',
    unique_key = 'HOST_ID'
    )
}}

SELECT
    HOST_ID,
    REPLACE(HOST_NAME,' ','_') as HOST_NAME,
    HOST_SINCE as HOST_SINCE,
    IS_SUPERHOST as IS_SUPERHOST,
    RESPONSE_RATE as RESPONSE_RATE,
    CASE
        WHEN RESPONSE_RATE > 95 THEN 'VERY GOOD'
        WHEN RESPONSE_RATE > 80 THEN 'GOOD'
        WHEN RESPONSE_RATE > 60 THEN 'FAIR'
        ELSE 'POOR'
    END as RESPONSE_RATE_TAG,
    CREATED_AT
from
    {{ ref('bronze_hosts') }}