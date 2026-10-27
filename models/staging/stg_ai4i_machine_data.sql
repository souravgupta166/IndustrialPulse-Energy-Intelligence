
select
    cast(source_record_id as bigint) as source_record_id,
    cast(machine_type as varchar) as machine_type,
    cast(air_temperature_k as double) as air_temperature_k,
    cast(process_temperature_k as double) as process_temperature_k,
    cast(rotational_speed_rpm as integer) as rotational_speed_rpm,
    cast(torque_nm as double) as torque_nm,
    cast(tool_wear_min as integer) as tool_wear_min,
    cast(machine_failure as integer) as machine_failure,
    cast(tool_wear_failure as integer) as tool_wear_failure,
    cast(heat_dissipation_failure as integer)
        as heat_dissipation_failure,
    cast(power_failure as integer) as power_failure,
    cast(overstrain_failure as integer) as overstrain_failure,
    cast(random_failure as integer) as random_failure
from {{ source('ai4i', 'raw_ai4i_machine_data') }}
