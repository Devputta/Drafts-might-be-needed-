{{ config(
    materialized = 'incremental',
    unique_key = 'LISTING_ID'
) }}

SELECT
    LISTING_ID,
    HOST_ID,
    PROPERTY_TYPE,
    ROOM_TYPE,
    CITY,
    COUNTRY,
    ACCOMMODATES,
    BEDROOMS,
    BATHROOMS,
    PRICE_PER_NIGHT,
    {{ tag('CAST(PRICE_PER_NIGHT as INT)') }} as PRICE_PER_NIGHT_TAG,
    CREATED_AT
    
from
    {{ ref('bronze_listings') }}