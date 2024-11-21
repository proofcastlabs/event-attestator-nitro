"""Store EVM blockchain state."""

from .. import ChainState


class EvmState(ChainState):
    """EvmState class."""

    def __init__(self, chain, events, event_consensus_threshold, rpcs):
        self.chain = chain
        self.events = events
        self.threshold = event_consensus_threshold
        self.rpcs = rpcs
