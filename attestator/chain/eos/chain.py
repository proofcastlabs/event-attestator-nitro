"""EOS blockchain representations."""

from dataclasses import dataclass

from ...utils import dataclass_to_field_set as to_set, format_set
from . import EosChainException


def check_mismatched_fields(json_dict, cls):
    """Throw if there's a field mismatch between the argument and the dataclass.

    Fields are mismatched when they are either not provided but requested, or provided but not
    requested."""
    provided_not_requested = set(json_dict) - to_set(cls, include_nullable=True)
    not_provided_requested = to_set(cls, include_nullable=False) - set(json_dict)

    if mismatched := provided_not_requested | not_provided_requested:
        raise EosChainException(
            f"Mismatched arguments for `{cls.__name__}`: {format_set(mismatched)}"
        )


@dataclass
class EosAuthorization:
    """EosAuthorization class."""

    actor: str
    permission: str

    @classmethod
    def from_json(cls, auth_json):
        """Create EosAuthorization from json."""
        check_mismatched_fields(auth_json, cls)

        return cls(**auth_json)


@dataclass
class EosAct:
    """EosAct class."""

    account: str
    authorization: list[EosAuthorization]
    data: dict
    name: str

    @classmethod
    def from_json(cls, act_json):
        """Create EosAct from json."""
        check_mismatched_fields(act_json, cls)

        auths = act_json["authorization"]
        act_json["authorization"] = [EosAuthorization.from_json(a) for a in auths]

        return cls(**act_json)


@dataclass
class EosAuth:
    """EosAuth class."""

    account: str
    sequence: str

    @classmethod
    def from_json(cls, auth_json):
        """Create EosAuth from json."""
        check_mismatched_fields(auth_json, cls)

        return cls(**auth_json)


@dataclass
class EosReceipt:
    """EosReceipt class."""

    auth_sequence: list[EosAuth]
    global_sequence: str
    receiver: str
    recv_sequence: str

    @classmethod
    def from_json(cls, rcpt_json):
        """Create EosReceipt from json."""
        check_mismatched_fields(rcpt_json, cls)

        auths = rcpt_json["auth_sequence"]
        rcpt_json["auth_sequence"] = [EosAuth.from_json(a) for a in auths]

        return cls(**rcpt_json)


@dataclass
class EosAction:
    # pylint: disable=too-many-instance-attributes
    """EosAction class."""
    abi_sequence: int
    act: EosAct
    act_digest: str
    action_ordinal: int
    block_id: str
    block_num: int
    code_sequence: int
    cpu_usage_us: int
    creator_action_ordinal: int
    global_sequence: int
    inline_count: int
    inline_filtered: int
    net_usage_words: int
    producer: str
    receipts: list[EosReceipt]
    signatures: list[str]
    timestamp: str
    trx_id: str

    elapsed: str | None = None

    @classmethod
    def from_json(cls, action_json):
        """Create EosAction from json."""
        # "@timestamp" duplicates "timestamp"
        del action_json["@timestamp"]

        check_mismatched_fields(action_json, cls)

        act = action_json["act"]
        action_json["act"] = EosAct.from_json(act)

        receipts = action_json["receipts"]
        action_json["receipts"] = [EosReceipt.from_json(r) for r in receipts]

        return cls(**action_json)


@dataclass
class EosTransaction:
    # pylint: disable=too-many-instance-attributes
    """EosTransaction class."""
    actions: list[EosAction]
    cached_lib: bool
    executed: bool
    last_indexed_block: int
    last_indexed_block_time: int
    lib: int
    query_time_ms: float
    trx_id: str

    cache_expires_in: int | None = None
    cached: bool | None = None

    @classmethod
    def from_json(cls, tx_json):
        """Create EosTransaction from json."""
        check_mismatched_fields(tx_json, cls)

        actions = tx_json["actions"]
        tx_json["actions"] = [EosAction.from_json(a) for a in actions]

        return cls(**tx_json)
