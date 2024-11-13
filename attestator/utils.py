"""Library utilities."""

import dataclasses


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
