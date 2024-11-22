"""Attestator client entrypoint."""

import argparse
import asyncio
import logging
import pprint
import socket
import sys


from .client import AttestatorClient


async def main(args):
    """Setup and run the attestator client."""
    parser = argparse.ArgumentParser(prog=__package__)
    parser.add_argument("cmd", help="command to pass to the attestator server")
    parser.add_argument(
        "cmd_args", nargs="*", help="command arguments to pass to the attestator server"
    )
    parser.add_argument(
        "-c",
        "--cid",
        type=int,
        default=socket.VMADDR_CID_HOST,
        help="enclave cid, ignored in debug mode",
    )
    parser.add_argument(
        "--host",
        default="localhost",
        help="connection host, used in debug mode",
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
    args = parser.parse_args(args)

    if args.debug:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((args.host, args.port))
    else:
        sock = socket.socket(socket.AF_VSOCK, socket.SOCK_STREAM)
        sock.connect((args.cid, args.port))

    reader, writer = await asyncio.open_connection(sock=sock)

    attestator_client = AttestatorClient()
    return await attestator_client.run(args.cmd, args.cmd_args, reader, writer)


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)

    ret = asyncio.run(main(sys.argv[1:]))

    pprint.pp(ret)
