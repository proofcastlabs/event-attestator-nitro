"""Interaction with blockchain endpoints and data."""

from ..crypto import generate_pk


class ChainException(Exception):
    """ChainException class."""


class RpcException(Exception):
    """ChainException class."""


EVM = "evm"
EOS = "eos"

CHAIN = {
    "ethereum": {"id": b"\x00" * 31 + b"\x01", "protocol": EVM},
    "ropsten": {"id": b"\x00" * 31 + b"\x03", "protocol": EVM},
    "goerli": {"id": b"\x00" * 31 + b"\x05", "protocol": EVM},
    "gnosis": {"id": b"\x00" * 31 + b"\x64", "protocol": EVM},
    "chiado": {"id": b"\x00" * 30 + b"\x27\xd8", "protocol": EVM},
    "sepolia": {"id": b"\x00" * 29 + b"\xaa\x36\xa7", "protocol": EVM},
    "eos": {
        # pylint: disable=line-too-long
        "id": b"\xac\xa3v\xf2\x06\xb8\xfc%\xa6\xedD\xdb\xdcfT|6\xc6\xc3>:\x11\x9f\xfb\xea\xef\x946B\xf0\xe9\x06",
        "protocol": EOS,
    },
    "jungle": {
        # pylint: disable=line-too-long
        "id": b"s\xe48Z'\x08\xe6\xd7\x04\x884\xfb\xc1\x07\x9f/\xab\xb1{<\x12[\x14j\xf48\x97\x1e\x90qlM",
        "protocol": EOS,
    },
}

CHAIN_PROTOCOL = {EVM: b"\x01", EOS: b"\x02"}


class ChainState:
    """ChainState class."""

    PK = None

    def __new__(cls, *_, **__):
        if ChainState.PK is None:
            ChainState.PK = generate_pk()
        return super().__new__(cls)
