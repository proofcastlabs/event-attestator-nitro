"""Attestator client entrypoint."""

import argparse
import asyncio
import logging
import socket


from .client import AttestatorClient


async def main():
    """Setup and run the attestator client."""
    parser = argparse.ArgumentParser(prog=__package__)
    parser.add_argument(
        "-c",
        "--cid",
        type=int,
        default=socket.VMADDR_CID_HOST,
        help="enclave cid",
    )
    parser.add_argument(
        "-p",
        "--port",
        type=int,
        default=8080,
        help="connection port",
    )
    parser.add_argument(
        "-d",
        "--debug",
        action="store_true",
        help="assume the client is connecting to a server started inside a normal docker container",
    )
    args = parser.parse_args()

    if args.debug:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect(("localhost", args.port))
    else:
        sock = socket.socket(socket.AF_VSOCK, socket.SOCK_STREAM)
        sock.connect((args.cid, args.port))

    reader, writer = await asyncio.open_connection(sock=sock)

    attestator_client = AttestatorClient()
    await attestator_client.run(reader, writer)


logging.basicConfig(level=logging.DEBUG)

asyncio.run(main())
