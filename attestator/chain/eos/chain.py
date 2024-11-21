"""EOS blockchain representations."""

from dataclasses import dataclass, field

from ...utils import check_mismatched_fields
from . import EosChainException


@dataclass
class EosAuthorization:
    """EosAuthorization class."""

    actor: str
    permission: str

    @classmethod
    def from_json(cls, auth_json):
        """Create EosAuthorization from json."""
        check_mismatched_fields(auth_json, cls, EosChainException)

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
        check_mismatched_fields(act_json, cls, EosChainException)

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
        check_mismatched_fields(auth_json, cls, EosChainException)

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
        check_mismatched_fields(rcpt_json, cls, EosChainException)

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
    creator_action_ordinal: int
    global_sequence: int
    producer: str
    receipts: list[EosReceipt]
    timestamp: str
    trx_id: str

    # Removed in equality comparison
    account_ram_deltas: list | None = field(default=None, compare=False)
    cpu_usage_us: int | None = field(default=None, compare=False)
    elapsed: str | None = field(default=None, compare=False)
    inline_count: int | None = field(default=None, compare=False)
    inline_filtered: int | None = field(default=None, compare=False)
    net_usage_words: int | None = field(default=None, compare=False)
    # Kept in equality comparison
    signatures: list[str] | None = None

    @classmethod
    def from_json(cls, action_json):
        """Create EosAction from json."""
        # "@timestamp" duplicates "timestamp"
        del action_json["@timestamp"]

        check_mismatched_fields(action_json, cls, EosChainException)

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
    cached_lib: bool = field(compare=False)
    executed: bool
    last_indexed_block: int = field(compare=False)
    last_indexed_block_time: int = field(compare=False)
    lib: int = field(compare=False)
    query_time_ms: float = field(compare=False)
    trx_id: str

    cache_expires_in: int | None = field(default=None, compare=False)
    cached: bool | None = field(default=None, compare=False)

    @classmethod
    def from_json(cls, tx_json):
        """Create EosTransaction from json."""
        check_mismatched_fields(tx_json, cls, EosChainException)

        actions = tx_json["actions"]
        tx_json["actions"] = [EosAction.from_json(a) for a in actions]

        return cls(**tx_json)
