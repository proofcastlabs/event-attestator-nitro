"""EVM rpc functionality."""

import ssl

import aiohttp

from aiohttp.client_exceptions import ClientError

from ...utils import format_tx_id, format_url
from .. import RpcException
from .chain import EvmTransactionReceipt


JSONRPC_PAYLOAD = {
    "jsonrpc": "2.0",
    "method": "eth_getTransactionReceipt",
    "id": 0,
}


async def get_evm_transaction(tx_id, endpoint, session=None, cert=None):
    """Get `tx_id` from `endpoint`, with optional aiohttp `session` and `cert` file, if provided."""
    close_session = False
    if session is None:
        session = aiohttp.ClientSession()
        # Since we're outside of the context manager, the session needs to be closed manually below
        close_session = True

    payload = {"params": [tx_id], **JSONRPC_PAYLOAD}
    ssl_context = True
    if cert is not None:
        ssl_context = ssl.create_default_context(cafile=cert)
    try:
        async with session.post(endpoint, json=payload, ssl=ssl_context) as resp:
            result = await resp.json()
            evm_tx = EvmTransactionReceipt.from_json(result["result"])
    except ClientError as exc:
        raise RpcException(
            f"Failed to get transaction {format_tx_id(tx_id)} from {format_url(endpoint)}: {exc}"
        ) from None
    finally:
        if close_session:
            await session.close()

    return evm_tx
