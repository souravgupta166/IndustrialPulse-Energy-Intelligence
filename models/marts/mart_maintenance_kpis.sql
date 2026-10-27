
with observations as (

    select *
    from {{ ref('int_machine_observations') }}

),

aggregated as (

    select
        machine_type,

        count(*) as total_observations,

        sum(machine_failure) as failure_observations,

        round(
            100.0 * sum(machine_failure) / nullif(count(*), 0),
            2
        ) as failure_rate_pct,

        round(avg(air_temperature_k), 2)
            as avg_air_temperature_k,

        round(avg(process_temperature_k), 2)
            as avg_process_temperature_k,

        round(avg(temperature_delta_k), 2)
            as avg_temperature_delta_k,

        round(avg(rotational_speed_rpm), 2)
            as avg_rotational_speed_rpm,

        round(avg(torque_nm), 2)
            as avg_torque_nm,

        round(avg(tool_wear_min), 2)
            as avg_tool_wear_min,

        sum(tool_wear_failure) as tool_wear_failure_flags,
        sum(heat_dissipation_failure)
            as heat_dissipation_failure_flags,
        sum(power_failure) as power_failure_flags,
        sum(overstrain_failure) as overstrain_failure_flags,
        sum(random_failure) as random_failure_flags

    from observations
    group by machine_type

)

select *
from aggregated
