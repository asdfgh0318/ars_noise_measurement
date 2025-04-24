from dataclasses import dataclass
import numbers
import operator
from typing import Callable, Protocol, Self, cast


@dataclass(frozen=True)
class FFTData:
    data: dict[float, float]


    @classmethod
    def num_operation(cls, op: Callable[[float, float], float], a: Self | float, b: Self | float):
        results = {}
        keyset: set[float] = set.intersection(*(set(x.data.keys()) for x in (a, b) if not isinstance(x, (float, int))))

        for k in keyset:
            val_a: float = a if isinstance(a, (float, int)) else a.data[k]
            val_b: float = b if isinstance(b, (float, int)) else b.data[k]
            results[k] = op(val_a, val_b)
        return cls(results)

    def __add__(self, other: Self):
        return self.num_operation(operator.add, self, other)

    def __mul__(self, other: float):
        return self.num_operation(operator.mul, self, other)


