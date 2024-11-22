"""Store EVM blockchain state."""

from ...crypto import sha256_and_sign_with_key
from ...utils import from_0x_hex, pad_bytes_with_zeros, to_0x_hex
from .. import CHAIN, CHAIN_PROTOCOL, EVM, ChainState


PROTOCOL = CHAIN_PROTOCOL[EVM]


class EvmState(ChainState):
    """EvmState class."""

    def __init__(self, chain, events, event_consensus_threshold, rpcs):
        self.chain = chain
        self.events = events
        self.threshold = event_consensus_threshold
        self.rpcs = rpcs

    @property
    def chain_id(self):
        """Return the chain id for the chain set for this state."""
        return CHAIN[self.chain]["id"]

    def filter_transaction(self, transaction):
        """Return alls the logs that match the events schema stored."""
        matching_logs = []
        for log in transaction.logs:
            for address, topic in self.events:
                if log.address == address.lower() and topic.lower() in log.topics:
                    matching_logs.append(log)
                    break
        return matching_logs

    def sign_logs(self, logs, version):
        """Sign `logs` for `version` with the standard encoding.

        Preimage encoding format:
            version:        1B
            protocol:       1B
            origin:         32B
            block-hash:     32B
            tx-hash:        32B
            event-payload:  varlen

        Event payload encoding format:
            address:        32B
            topics:         128B
            log-data:       varlen
        """
        signed_logs = []
        for log in logs:
            block_hash, tx_hash, address, log_data = from_0x_hex(
                log.blockHash, log.transactionHash, log.address, log.data
            )

            topics = pad_bytes_with_zeros(
                b"".join(from_0x_hex(*log.topics)), 128, pad_right=True
            )

            event_payload = address + topics + log_data

            preimage = (
                version
                + PROTOCOL
                + self.chain_id
                + block_hash
                + tx_hash
                + event_payload
            )

            event_id, signature = sha256_and_sign_with_key(preimage, self.PK)
            # Representing a signature as R + S + V, for Evm
            signature = (
                signature.r.to_bytes(32)
                + signature.s.to_bytes(32)
                + signature.v.to_bytes()
            )

            (
                event_id,
                signature,
                version,
                protocol,
                chain_id,
                event_payload,
            ) = to_0x_hex(
                event_id,
                signature,
                version,
                PROTOCOL,
                self.chain_id,
                event_payload,
            )

            signed_logs.append(
                {
                    "version": version,
                    "protocol": protocol,
                    "origin": chain_id,
                    "data": log.data,
                    "tx_id_hash": log.transactionHash,
                    "block_id_hash": log.blockHash,
                    "event_payload": event_payload,
                    "event_id": event_id,
                    "signature": signature,
                    "public_key": self.PK.address,
                }
            )
        return signed_logs
