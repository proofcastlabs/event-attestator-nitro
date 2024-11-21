"""EVM blockchain representations."""

from dataclasses import dataclass, field

from ...utils import check_mismatched_fields
from . import EvmChainException


@dataclass
class EvmLog:
    """EvmLog class."""

    # pylint: disable=invalid-name, too-many-instance-attributes
    address: str
    blockHash: str
    blockNumber: str
    data: str
    logIndex: str
    removed: bool
    topics: list[str]
    transactionHash: str
    transactionIndex: str

    blockTimestamp: str | None = field(default=None, compare=False)

    @classmethod
    def from_json(cls, log_json):
        """Create EvmLog from json."""
        check_mismatched_fields(log_json, cls, EvmChainException)

        return cls(**log_json)


@dataclass
class EvmTransactionReceipt:
    """EvmTransactionReceipt class."""

    # pylint: disable=invalid-name, too-many-instance-attributes
    blockHash: str
    blockNumber: str
    contractAddress: str | None
    cumulativeGasUsed: str
    effectiveGasPrice: str
    from_: str
    gasUsed: str
    logs: list[EvmLog]
    logsBloom: str
    status: str
    to: str
    transactionHash: str
    transactionIndex: str
    type_: str

    blobGasUsed: str | None = field(default=None, compare=False)

    @classmethod
    def from_json(cls, rcpt_json):
        """Create EvmTransactionReceipt from json."""
        try:
            rcpt_json["from_"] = rcpt_json.pop("from")
        except KeyError:
            pass
        try:
            rcpt_json["type_"] = rcpt_json.pop("type")
        except KeyError:
            pass

        check_mismatched_fields(rcpt_json, cls, EvmChainException)

        logs = rcpt_json["logs"]
        rcpt_json["logs"] = [EvmLog.from_json(l) for l in logs]

        return cls(**rcpt_json)
