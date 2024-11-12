"""Attestator client."""

import logging


from ..messages import (
    ERROR_RESPONSE,
    INVALID_REQUEST_TYPE,
    PING,
    VSockRequest,
    VSockResponse,
    dict_to_vsock_message,
    vsock_message_to_dict,
)


logger = logging.getLogger(__name__)


class AttestatorClient:
    """AttestatorClient class."""

    async def run(self, cmd, cmd_args, reader, writer):
        """Run `cmd` on the server through the given `reader` and `writer` pair."""
        address, port = writer.get_extra_info("socket").getsockname()
        logger.info("Client started on %s:%d", address, port)

        if cmd == PING:
            ping = VSockRequest(request_type=PING, args=[]).as_dict()
            logger.info("Sending ping message")
            writer.writelines([dict_to_vsock_message(ping)])
            await writer.drain()

            return VSockResponse.from_json(
                vsock_message_to_dict(await reader.readline())
            )
        return VSockResponse(
            response_type=ERROR_RESPONSE, response=[INVALID_REQUEST_TYPE]
        )
