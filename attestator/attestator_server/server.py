"""Attestator server."""

import logging
import os

import toml

from ..crypto import pk_to_pub
from ..chain import ChainException, ChainState
from ..chain.core import create_chain_state_from_config, sign_events
from ..messages import (
    ERROR_RESPONSE,
    GET_ATTESTATION,
    INVALID_REQUEST_TYPE,
    NOT_ENOUGH_ARGUMENTS,
    NO_CONFIG,
    PING,
    PONG,
    SIGN_EVENT,
    SUCCESS_RESPONSE,
    UNINITIALIZED,
    VSockRequest,
    VSockResponse,
    dict_to_vsock_message,
    vsock_message_to_dict,
)


ATTESTATION_EXEC = "./attestation"
SUCCESS_PREFIX = "Success:"
VERSION = b"\x01"


logger = logging.getLogger(__name__)


class AttestatorServer:
    """AttestatorServer class."""

    def __init__(self, state, config=None, cert=None):
        self.state = state
        self.config = config
        self.cert = cert

    @classmethod
    def from_config_toml(cls, config, cert=None):
        """Build an AttestatorServer with the given configuration and optional `cert` file."""
        config_toml = toml.load(config)

        state = {}
        for chain, chain_config in config_toml["networks"].items():
            state[chain] = create_chain_state_from_config(chain, chain_config)

        return cls(state, config, cert)

    def get_attestation(self):
        """Return NSM-backed attestation, including the event signing key and the configuration."""
        if self.config is None:
            return VSockResponse(response_type=ERROR_RESPONSE, response=[NO_CONFIG])
        if ChainState.PK is None:
            return VSockResponse(response_type=ERROR_RESPONSE, response=[UNINITIALIZED])

        # The attestation binary expects user data, nonce and public key arguments. I'm reading the
        # configuration directly from its file to avoid handling escapes
        attestation_out = os.popen(
            f'{ATTESTATION_EXEC} "$(cat {self.config})" "" {ChainState.PK.address}'
        ).read()

        if (success := attestation_out.removeprefix(SUCCESS_PREFIX)) != attestation_out:
            return VSockResponse(
                response_type=SUCCESS_RESPONSE,
                response=[
                    ChainState.PK.address,
                    pk_to_pub(ChainState.PK),
                    success.strip(),
                ],
            )
        return VSockResponse(response_type=ERROR_RESPONSE, response=[attestation_out])

    async def sign_events(self, request):
        """Sign appropriate events with the corresponding chain state information."""
        try:
            chain, *args = request.args
        except ValueError:
            return VSockResponse(
                response_type=ERROR_RESPONSE, response=[NOT_ENOUGH_ARGUMENTS]
            )

        if (chain_state := self.state.get(chain)) is None:
            return VSockResponse(
                response_type=ERROR_RESPONSE, response=[UNINITIALIZED, chain]
            )

        try:
            signed_events = await sign_events(
                args, chain, chain_state, VERSION, self.cert
            )
        except ChainException as exc:
            return VSockResponse(response_type=ERROR_RESPONSE, response=[str(exc)])
        return VSockResponse(response_type=SUCCESS_RESPONSE, response=signed_events)

    async def run(self, reader, writer):
        """Run the server once a stream as been established."""
        address, port = writer.get_extra_info("socket").getsockname()
        logger.info("Server started on %s:%d", address, port)
        async for msg in reader:
            request = VSockRequest.from_json(vsock_message_to_dict(msg))
            if request.request_type == GET_ATTESTATION:
                resp = self.get_attestation()
            elif request.request_type == PING:
                resp = VSockResponse(response_type=SUCCESS_RESPONSE, response=[PONG])
            elif request.request_type == SIGN_EVENT:
                resp = await self.sign_events(request)
            else:
                resp = VSockResponse(
                    response_type=ERROR_RESPONSE, response=[INVALID_REQUEST_TYPE]
                )
            resp = resp.as_dict()

            writer.writelines([dict_to_vsock_message(resp)])
            await writer.drain()
