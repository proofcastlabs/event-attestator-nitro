"""Attestator client."""

import logging


from ..messages import (
    PING,
    PONG,
    SUCCESS_RESPONSE,
    VSockRequest,
    VSockResponse,
    dict_to_vsock_message,
    vsock_message_to_dict,
)


logger = logging.getLogger(__name__)


class AttestatorClient:
    """AttestatorClient class."""

    async def run(self, reader, writer):
        """Run the client with the given `reader` and `writer` pair."""
        address, port = writer.get_extra_info("socket").getsockname()
        logger.info("Client started on %s:%d", address, port)

        ping = VSockRequest(request_type=PING, args=[]).as_dict()
        logger.info("Sending ping message")
        writer.writelines([dict_to_vsock_message(ping)])
        await writer.drain()

        pong = VSockResponse.from_json(vsock_message_to_dict(await reader.readline()))
        if pong.response_type == SUCCESS_RESPONSE and pong.response[0] == PONG:
            logger.info("Received pong successfully")
