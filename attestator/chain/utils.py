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
