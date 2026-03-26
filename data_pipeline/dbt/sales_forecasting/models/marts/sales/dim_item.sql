-- depends_on: {{ ref('stg_sales') }}
{{ config(materialized='table') }}

select distinct
    item_id
from {{ ref('stg_sales') }}
