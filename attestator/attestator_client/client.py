"""Attestator client."""

import logging


from ..messages import (
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

        request = VSockRequest(request_type=cmd, args=cmd_args).as_dict()
        logger.info("Sending request")
        writer.writelines([dict_to_vsock_message(request)])
        writer.write_eof()
        await writer.drain()

        resp = await reader.readline()
        logger.info("Received response %s", resp)

        return VSockResponse.from_json(vsock_message_to_dict(resp))
