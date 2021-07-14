"""Inspect PMSx003 data fields"""

from dataclasses import fields
from typing import Dict

from pms.core import Sensor
from pms.core.types import ObsData


def types(obs: ObsData) -> Dict[str, str]:
    """return a dictionary containing the type of each data field"""
    return {field.name: field.type.__name__ for field in fields(obs)}


print(types(Sensor["PMSx003"].Data))
