"""EOS rpc functionality."""

import ssl

import aiohttp

from aiohttp.client_exceptions import ClientError

from ...utils import format_tx_id, format_url
from .. import RpcException
from .chain import EosTransaction

TX_ENDPOINT = "/v2/history/get_transaction"


async def get_eos_transaction(tx_id, endpoint, session=None, cert=None):
    """Get `tx_id` from `endpoint`, with optional aiohttp `session` and `cert` file, if provided."""
    close_session = False
    if session is None:
        session = aiohttp.ClientSession()
        # Since we're outside of the context manager, the session needs to be closed manually below
        close_session = True

    if endpoint.endswith("/"):
        endpoint = endpoint[:-1]
    endpoint += TX_ENDPOINT

    ssl_context = True
    if cert is not None:
        ssl_context = ssl.create_default_context(cafile=cert)
    try:
        async with session.get(endpoint, params={"id": tx_id}, ssl=ssl_context) as resp:
            eos_tx = EosTransaction.from_json(await resp.json())
    except ClientError as exc:
        raise RpcException(
            f"Failed to get transaction {format_tx_id(tx_id)} from {format_url(endpoint)}: {exc}"
        ) from None
    finally:
        if close_session:
            await session.close()

    return eos_tx
