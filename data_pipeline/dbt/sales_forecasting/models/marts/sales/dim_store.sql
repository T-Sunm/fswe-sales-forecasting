-- depends_on: {{ ref('stg_key') }}
{{ config(materialized='table') }}

select distinct
    store_id,
    station_id
from {{ ref('stg_key') }}
