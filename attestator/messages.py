"""VSock message conversions, representation and constants."""

import dataclasses
import json


def dict_to_vsock_message(dct):
    """Dump `dct` as json, encode and add a newline character."""
    return json.dumps(dct).encode() + b"\n"


def vsock_message_to_dict(msg):
    """Strip newline character, decode and load `msg` as json."""
    return json.loads(msg[:-1].decode())


# This doesn't tecnically need to be a dataclass, but this pleases the code analyzer
# (`dataclass.asdict` requires to be passed a dataclass instance)
@dataclasses.dataclass
class VsockMessage:
    """VsockMessage class."""

    def as_dict(self):
        """Turn the dataclass into a dictionary."""
        return dataclasses.asdict(self)

    @classmethod
    def from_json(cls, msg_json):
        """Create VSockMessage from json."""
        return cls(**msg_json)


# Message types
PING = "ping"
PONG = "pong"


@dataclasses.dataclass
class VSockRequest(VsockMessage):
    """VSockRequest class."""

    request_type: str
    args: list


ERROR_RESPONSE = "error"
INVALID_REQUEST_TYPE = "invalid-request-type"
SUCCESS_RESPONSE = "success"


@dataclasses.dataclass
class VSockResponse(VsockMessage):
    """VSockResponse class."""

    response_type: str
    response: list
