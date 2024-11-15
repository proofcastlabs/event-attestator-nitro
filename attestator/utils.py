"""Library utilities."""

import dataclasses

from urllib.parse import urlparse


def dataclass_to_field_set(dataclass, include_nullable):
    """Extract a set of fields names from a dataclass.

    If `include_nullable` is set to `False`, the returned list will not contain names for fields
    that default to `None`."""
    fields = dataclasses.fields(dataclass)
    if not include_nullable:
        fields = tuple(f for f in fields if f.default is not None)

    return {f.name for f in fields}


def format_set(_set):
    """Format set elements as string."""
    return ", ".join(map(lambda e: f'"{e}"', _set))


MAX_TX_ID_SIZE = 10
assert MAX_TX_ID_SIZE > 1


def format_tx_id(tx_id):
    """Shrink id size to `MAX_TX_ID_SIZE`."""
    if len(tx_id) > MAX_TX_ID_SIZE:
        head = MAX_TX_ID_SIZE // 2
        tail = MAX_TX_ID_SIZE - head

        tx_id = tx_id[:head] + "..." + tx_id[-tail:]

    return tx_id


def format_url(url):
    """Extract the authority portion from `url`."""
    return urlparse(url).netloc or url


def left_pad_bytes_with_zeros(message, padding):
    """Return `message` left padded with zeros, up to `padding` length."""
    padding = max(padding - len(message), 0)

    return b"\x00" * padding + message


def to_0x_hex(*args):
    """Return `args` bytes as the corresponding, 0x-prefixed, hexes."""
    return ["0x" + arg.hex() for arg in args]
