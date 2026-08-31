{{ 
    config(
        materialized = 'incremental', 
        unique_key = 'BOOKING_ID'
        )
}}

SELECT
    BOOKING_ID,
    LISTING_ID,
    BOOKING_DATE,
    {{ multiply('NIGHTS_BOOKED','BOOKING_AMOUNT',2) }} as TOTAL_AMOUNT,
    CLEANING_FEE,
    SERVICE_FEE,
    BOOKING_STATUS,
    CREATED_AT,
    
from
    {{ ref('bronze_bookings') }}