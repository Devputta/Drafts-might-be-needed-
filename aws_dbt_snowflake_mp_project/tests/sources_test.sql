{{
  config(
    severity = 'warn'
    )
}}

SELECT
    1
FROM 
    {{ source('stagings', 'bookings') }}
WHERE
    BOOKING_AMOUNT < 200