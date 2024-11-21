"""Store EVM blockchain state."""

from .. import ChainState


class EvmState(ChainState):
    """EvmState class."""

    def __init__(self, chain, events, event_consensus_threshold, rpcs):
        self.chain = chain
        self.events = events
        self.threshold = event_consensus_threshold
        self.rpcs = rpcs

    def filter_transaction(self, transaction):
        """Return alls the logs that match the events schema stored."""
        matching_logs = []
        for log in transaction.logs:
            for address, topic in self.events:
                if log.address == address.lower() and topic.lower() in log.topics:
                    matching_logs.append(log)
                    break
        return matching_logs
