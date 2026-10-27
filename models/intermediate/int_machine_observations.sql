
with staging as (

    select *
    from {{ ref('stg_ai4i_machine_data') }}

),

enriched as (

    select
        source_record_id,
        machine_type,

        air_temperature_k,
        process_temperature_k,
        process_temperature_k - air_temperature_k
            as temperature_delta_k,

        rotational_speed_rpm,
        torque_nm,
        tool_wear_min,

        machine_failure,
        tool_wear_failure,
        heat_dissipation_failure,
        power_failure,
        overstrain_failure,
        random_failure,

        (
            tool_wear_failure
            + heat_dissipation_failure
            + power_failure
            + overstrain_failure
            + random_failure
        ) as failure_mode_count,

        case
            when machine_failure = 1 then true
            else false
        end as is_machine_failure,

        case
            when tool_wear_failure = 1 then 'tool_wear'
            when heat_dissipation_failure = 1 then 'heat_dissipation'
            when power_failure = 1 then 'power'
            when overstrain_failure = 1 then 'overstrain'
            when random_failure = 1 then 'random'
            when machine_failure = 1 then 'other_or_unclassified'
            else 'no_recorded_failure'
        end as primary_failure_category

    from staging

)

select *
from enriched
