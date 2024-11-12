"""Attestator server entrypoint."""

import argparse
import asyncio
import logging
import socket

from .server import AttestatorServer


SOCK_BACKLOG = 10


async def main():
    """Setup and run the attestator server."""
    parser = argparse.ArgumentParser(prog=__package__)
    parser.add_argument(
        "-p",
        "--port",
        type=int,
        default=8080,
        help="listening port",
    )
    parser.add_argument(
        "-d",
        "--debug",
        action="store_true",
        help="assume the server is started inside a normal docker container",
    )
    args = parser.parse_args()

    if args.debug:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind(("0.0.0.0", args.port))
    else:
        sock = socket.socket(socket.AF_VSOCK, socket.SOCK_STREAM)
        sock.bind((socket.VMADDR_CID_ANY, args.port))

    sock.listen(SOCK_BACKLOG)

    attestator_server = AttestatorServer()

    server = await asyncio.start_server(attestator_server.run, sock=sock)

    await server.serve_forever()


logging.basicConfig(level=logging.DEBUG)

asyncio.run(main())
