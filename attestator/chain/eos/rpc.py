"""EOS rpc functionality."""

import aiohttp

from aiohttp.client_exceptions import ClientError

from ...utils import format_tx_id, format_url
from .. import RpcException
from .chain import EosTransaction


async def get_eos_transaction(tx_id, endpoint, session=None):
    """Get `tx_id` from `endpoint`, with an optional aiohttp `session`, if provided."""
    close_session = False
    if session is None:
        session = aiohttp.ClientSession()
        # Since we're outside of the context manager, the session needs to be closed manually below
        close_session = True

    try:
        async with session.get(endpoint, params={"id": tx_id}) as resp:
            eos_tx = EosTransaction.from_json(await resp.json())
    except ClientError as exc:
        raise RpcException(
            f"Failed to get transaction {format_tx_id(tx_id)} from {format_url(endpoint)}: {exc}"
        ) from None
    finally:
        if close_session:
            await session.close()

    return eos_tx
