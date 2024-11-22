"""Library utilities."""

import dataclasses

from urllib.parse import urlparse


def check_mismatched_fields(json_dict, dataclass, exception):
    """Throw `exception` if there's a field mismatch between the `json_dict` and the `dataclass`.

    Fields are mismatched when they are either not provided but requested, or provided but not
    requested."""
    provided_not_requested = set(json_dict) - dataclass_to_field_set(
        dataclass, include_nullable=True
    )
    not_provided_requested = dataclass_to_field_set(
        dataclass, include_nullable=False
    ) - set(json_dict)

    if mismatched := provided_not_requested | not_provided_requested:
        raise exception(
            f"Mismatched arguments for `{dataclass.__name__}`: {format_set(mismatched)}"
        )


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


def pad_bytes_with_zeros(message, padding, pad_right=False):
    """Return `message` padded with zeros, up to `padding` length."""
    padding = max(padding - len(message), 0)

    if pad_right:
        return message + b"\x00" * padding
    return b"\x00" * padding + message


def from_0x_hex(*args):
    """Return 0x-prefixed `args` hexes as the corresponding bytes."""
    return [bytes.fromhex(arg[2:]) for arg in args]


def to_0x_hex(*args):
    """Return `args` bytes as the corresponding, 0x-prefixed, hexes."""
    return ["0x" + arg.hex() for arg in args]
