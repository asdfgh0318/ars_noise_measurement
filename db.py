from typing import Optional
from dataclasses import dataclass


@dataclass
class MeasurementAttributes:
    motor: Optional[str] = None
    prop: Optional[str] = None
    description: Optional[str] = None

class Database:

