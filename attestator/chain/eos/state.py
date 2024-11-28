"""Store EOS blockchain state."""

import json

from ...crypto import pk_to_pub, sha256_and_sign_with_key
from ...utils import pad_bytes_with_zeros, to_0x_hex
from .. import CHAIN, CHAIN_PROTOCOL, EOS, ChainState


PROTOCOL = CHAIN_PROTOCOL[EOS]


def encode_event_data(data):
    """Serialize `data` as bytes."""
    return json.dumps(data, separators=(",", ":"), sort_keys=True).encode()


class EosState(ChainState):
    """EosState class."""

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
        """Return alls the actions that match the events schema stored."""
        matching_actions = []
        for action in transaction.actions:
            for account, name in self.events:
                if action.act.account == account and action.act.name == name:
                    matching_actions.append(action)
                    break
        return matching_actions

    def sign_actions(self, actions, version):
        """Sign `actions` for `version` with the standard encoding.

        Preimage encoding format:
            version:        1B
            protocol:       1B
            origin:         32B
            block-hash:     32B
            tx-hash:        32B
            event-payload:  varlen

        Event payload encoding format:
            event-account:  32B
            event-action:   128B
            event-data:     varlen
        """
        signed_actions = []
        for action in actions:
            for account, name in self.events:
                if action.act.account == account and action.act.name == name:
                    data = action.act.data
                    break
            else:
                continue

            block_hash = bytes.fromhex(action.block_id)
            tx_hash = bytes.fromhex(action.trx_id)

            event_account = pad_bytes_with_zeros(account.encode(), 32)
            event_action = pad_bytes_with_zeros(name.encode(), 32) + b"\x00" * 32 * 3
            event_data = encode_event_data(data)

            event_payload = event_account + event_action + event_data

            preimage = (
                version
                + PROTOCOL
                + self.chain_id
                + block_hash
                + tx_hash
                + event_payload
            )

            event_id, signature = sha256_and_sign_with_key(preimage, self.PK)

            (
                event_id,
                r,
                s,
                v,
                version,
                protocol,
                chain_id,
                tx_id_hash,
                block_id_hash,
                event_payload,
            ) = to_0x_hex(
                event_id,
                signature.r.to_bytes(32),
                signature.s.to_bytes(32),
                signature.v.to_bytes(),
                version,
                PROTOCOL,
                self.chain_id,
                tx_hash,
                block_hash,
                event_payload,
            )

            signed_actions.append(
                {
                    "version": version,
                    "protocol": protocol,
                    "origin": chain_id,
                    "data": data,
                    "tx_id_hash": tx_id_hash,
                    "block_id_hash": block_id_hash,
                    "event_payload": event_payload,
                    "event_id": event_id,
                    "signature": {"r": r, "s": s, "v": v},
                    "public_key": pk_to_pub(self.PK),
                }
            )
        return signed_actions
