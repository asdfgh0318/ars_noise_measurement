from typing import Callable, Protocol, Self, Sequence


class Interpolable(Protocol):
    def __add__(self: Self, other: Self, /) -> Self: ...
    def __mul__(self: Self, other: float, /) -> Self: ...

def lin_interpolate[T: Interpolable](arg: float, arg_l: float, arg_h: float, val_l: T, val_h: T) -> T:
    if arg_l == arg_h:
        return val_l

    w_l = (arg_h - arg) / (arg_h - arg_l)
    w_h = (arg - arg_l) / (arg_h - arg_l)

    return val_l * w_l + val_h * w_h

# sequence assumed to be in order
def find_args_binary[T](seq: Sequence[T], key: Callable[[T], float], val: float) -> tuple[T, T]:
    # print(seq)
    if len(seq) < 2:
        raise ValueError()
    if val < key(seq[0]):
        raise ValueError()
    if val > key(seq[-1]):
        raise ValueError()
    if len(seq) == 2:
        return (seq[0], seq[1])

    index_mid = len(seq)//2
    val_mid = key(seq[index_mid])
    # print(f'{index_mid}: {val_mid}')
    if val > val_mid:
        return find_args_binary(seq[index_mid:], key, val)
    else:
        return find_args_binary(seq[:index_mid+1], key, val)

def interp_keyed[T, U: Interpolable](seq: Sequence[T], key_key: Callable[[T], float], key_val: Callable[[T], U], x: float) -> U:
    args = find_args_binary(seq, key_key, x)
    karg_l, karg_h = map(key_key, args)
    val_l, val_h = map(key_val, args)
    return lin_interpolate(x, karg_l, karg_h, val_l, val_h)
