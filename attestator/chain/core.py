"""Core chain functionality."""

import asyncio

from . import CHAIN, EOS, EVM, ChainException
from .eos import EosChainException
from .eos.state import EosState
from .eos.rpc import get_eos_transaction
from .evm.state import EvmState


def create_chain_state_from_config(chain, config):
    """Return a ChainState instance from the given configuration."""
    chain = chain.lower()
    if chain not in CHAIN:
        raise ChainException(f"Chain {chain} not supported")

    protocol = CHAIN[chain]["protocol"]
    if protocol in (EVM, EOS):
        threshold = config["consensus_threshold"]
        endpoints = config["endpoints"]
        if len(endpoints) // 2 + 1 > threshold:
            raise ChainException(
                f"Consensus threshold too small: threshold {threshold}, endpoints {len(endpoints)}"
            )

        for event in config["events"]:
            if len(event) != 2 and not all((isinstance(e, str) for e in event)):
                if protocol == EVM:
                    evt_fmt = "(address, eventTopic)"
                else:  # if protocol == EOS
                    evt_fmt = "(account, actionName)"
                raise ChainException(
                    "Evm events must be defined as the following "
                    "tuple of strings: " + evt_fmt
                )

        if protocol == EVM:
            return EvmState(chain, config["events"], threshold, endpoints)
        # elif protocol == EOS
        return EosState(chain, config["events"], threshold, endpoints)
    raise ChainException(f"Protocol {protocol} not supported")


def find_consensus_element(data, threshold):
    """Return an element from `data` if at least `threshold` elements match it.

    `threshold` needs to be at least `len(data) // 2 + 1` to make sense."""
    # If no consensus element is found in the first half + 1 of the data, none will be
    # I'm checking half **plus one** to cover for odd `data` lengths
    cutoff = len(data) // 2 + 1
    consensus = None
    for idx, e in enumerate(data[:cutoff]):
        counter = 1
        # Checking forward only, no point in checking prior elements, since I already did
        for ee in data[idx + 1 :]:
            # This works by overloading `==` with `__eq__`
            if e == ee:
                counter += 1
        if counter >= threshold:
            consensus = e
            break
    return consensus


async def sign_events(events, chain, state, version):
    """Sign `events` on `chain` with the given chain `state`."""
    protocol = CHAIN[chain]["protocol"]

    if protocol == EVM:
        pass
    if protocol == EOS:
        try:
            (tx_id,) = events
        except ValueError:
            raise EosChainException(
                f"Invalid event details: expected `[transaction_id]`, received {events}"
            ) from None

        txs = await asyncio.gather(
            *(get_eos_transaction(tx_id, rpc) for rpc in state.rpcs),
            return_exceptions=True,
        )

        filtered_txs = [tx for tx in txs if not isinstance(tx, Exception)]

        if (consensus := find_consensus_element(filtered_txs, state.threshold)) is None:
            txs_str = ", ".join(
                map(str, filter(lambda tx: isinstance(tx, Exception), txs))
            )
            raise EosChainException(f"No consensus found, endpoint returns: {txs_str}")

        filtered_actions = state.filter_transaction(consensus)

        return state.sign_actions(filtered_actions, version)

    # This is here mostly for the linter, an initialized chain should not belong to an unsupported
    # protocol
    raise ChainException(f"Protocol {protocol} not supported")
