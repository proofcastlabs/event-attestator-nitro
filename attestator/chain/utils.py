"""Chain utilities."""

from . import CHAIN, EOS, EVM, ChainException
from .eos.state import EosState


def create_chain_state_from_config(chain, config):
    """Return a ChainState instance from the given configuration."""
    chain = chain.lower()
    if chain not in CHAIN:
        raise ChainException(f"Chain {chain} not supported")

    protocol = CHAIN[chain]["protocol"]
    if protocol == EVM:
        pass
    if protocol == EOS:
        return EosState(
            chain, config["events"], config["consensus_threshold"], config["endpoints"]
        )
    raise ChainException(f"Protocol {protocol} not supported")
