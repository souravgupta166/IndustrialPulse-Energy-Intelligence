
select *
from {{ ref('mart_maintenance_kpis') }}
where
    total_observations <= 0
    or failure_observations < 0
    or failure_observations > total_observations
    or failure_rate_pct < 0
    or failure_rate_pct > 100
