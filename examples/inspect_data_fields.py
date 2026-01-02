"""Inspect sensor data fields"""

from dataclasses import fields

from pms.core import Sensor
from pms.core.types import ObsData


def field_types(obs: ObsData) -> dict[str, str]:
    """return a dictionary containing the type of each data field"""

    return {
        field.name: field.type.__name__ if hasattr(field.type, "__name__") else str(field.type)
        for field in fields(obs)
    }


for sensor in Sensor:
    print(sensor)
    print(field_types(sensor.Data))
