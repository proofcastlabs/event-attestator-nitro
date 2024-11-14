"""Attestator server."""

import logging

import toml

from ..chain.utils import create_chain_state_from_config
from ..messages import (
    ERROR_RESPONSE,
    INVALID_REQUEST_TYPE,
    PING,
    PONG,
    SUCCESS_RESPONSE,
    VSockRequest,
    VSockResponse,
    dict_to_vsock_message,
    vsock_message_to_dict,
)


logger = logging.getLogger(__name__)


class AttestatorServer:
    """AttestatorServer class."""

    def __init__(self, state):
        self.state = state

    @classmethod
    def from_config_toml(cls, config):
        """Build an AttestatorServer with the given configuration."""
        config = toml.load(config)

        state = {}
        for chain, chain_config in config["networks"].items():
            state[chain] = create_chain_state_from_config(chain, chain_config)

        return cls(state)

    async def run(self, reader, writer):
        """Run the server once a stream as been established."""
        address, port = writer.get_extra_info("socket").getsockname()
        logger.info("Server started on %s:%d", address, port)
        async for msg in reader:
            request = VSockRequest.from_json(vsock_message_to_dict(msg))
            if request.request_type == PING:
                resp = VSockResponse(response_type=SUCCESS_RESPONSE, response=[PONG])
            else:
                resp = VSockResponse(
                    response_type=ERROR_RESPONSE, response=[INVALID_REQUEST_TYPE]
                )
            resp = resp.as_dict()

            writer.writelines([dict_to_vsock_message(resp)])
            await writer.drain()
