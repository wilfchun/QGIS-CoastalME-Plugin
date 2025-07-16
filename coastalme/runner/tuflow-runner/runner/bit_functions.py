# testBit() returns a nonzero result, 2**offset, if the bit at 'offset' is one.

def test_bit(int_type, offset):
    mask = 1 << offset
    return int_type & mask


# setBit() returns an integer with the bit at 'offset' set to 1.

def set_bit(int_type, offset):
    mask = 1 << offset
    return int_type | mask


# clearBit() returns an integer with the bit at 'offset' cleared.

def clear_bit(int_type, offset):
    mask = ~(1 << offset)
    return int_type & mask


# toggleBit() returns an integer with the bit at 'offset' inverted, 0 -> 1 and 1 -> 0.

def toggle_bit(int_type, offset):
    mask = 1 << offset
    return int_type ^ mask
