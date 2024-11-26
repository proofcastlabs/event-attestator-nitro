"""Traffic forwarding outside an enclave through the VSock."""

import argparse
import asyncio
import socket
import sys
import urllib.parse

import toml


class ForwardException(Exception):
    """ForwardException class."""


def range_generator(start):
    """Infinitely yield elemens of the integer sequence starting from `start`."""
    while True:
        yield start
        start += 1


SOCK_BUF = 1024


class ForwardServer:
    """ForwardServer class."""

    def __init__(self, rpc_map, host, debug_mode):
        self.rpc_map = rpc_map
        self.host = host
        self.debug_mode = debug_mode

    @classmethod
    def from_config_toml(cls, config, host, starting_port, debug_mode):
        """Build an ForwardServer with the given configuration."""
        config_toml = toml.load(config)

        rpcs = set()
        for chain_config in config_toml["networks"].values():
            rpcs.update(
                urllib.parse.urlparse(e).netloc for e in chain_config["endpoints"]
            )
        rpcs = dict(zip(sorted(rpcs), range_generator(starting_port)))

        return cls(rpcs, host, debug_mode)

    async def run(self, reader, writer):
        """Run the server once a stream as been established."""
        request_url_buf = await reader.read(SOCK_BUF)
        for rpc, port in self.rpc_map.items():
            if rpc.encode() in request_url_buf:
                break
        else:
            raise ForwardException("Request url not configured")

        if self.debug_mode:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        else:
            sock = socket.socket(socket.AF_VSOCK, socket.SOCK_STREAM)
        sock.connect((self.host, port))

        reader_out, writer_out = await asyncio.open_connection(sock=sock)
        writer_out.write(request_url_buf)
        await writer_out.drain()

        await asyncio.gather(forward(reader, writer_out), forward(reader_out, writer))


async def forward(reader, writer):
    """Forward the `reader` stream into the `writer`, until it's closed.

    Some hosts might misbehave and close their end of the socket without so much as an EOF. Drop the
    ensuing `OSError`."""
    try:
        while msg := await reader.read(SOCK_BUF):
            writer.write(msg)
            await writer.drain()
    except OSError:
        pass

    try:
        writer.close()
        await writer.wait_closed()
    except OSError:
        pass


EXPORT_AS_VSOCK_PROXY_SCRIPT = "--export-as-vsock-proxy-script"


async def main(args):
    """Run traffic forwarder."""
    parser = argparse.ArgumentParser(prog="attestator.traffic_forwarder")
    parser.add_argument("config", help="attestator blockchain configuration file")
    parser.add_argument(
        "-c",
        "--cid",
        type=int,
        default=3,
        help="enclave cid, needs to correspond to a vsock \
              proxy on the other side, ignored in debug mode",
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
        default=443,
        help="incoming connection port",
    )
    parser.add_argument(
        "-o",
        "--out-port",
        type=int,
        default=8000,
        help="outgoing connection port starting range",
    )
    parser.add_argument(
        "-d",
        "--debug",
        action="store_true",
        help="assume the client is connecting to a server started inside a normal docker container",
    )
    export_group = parser.add_mutually_exclusive_group()
    export_group.add_argument(
        "--export-as-allow-list",
        action="store_true",
        help="print to stdout a vsock proxy-compatible allow-list",
    )
    export_group.add_argument(
        "--export-as-hosts",
        action="store_true",
        help="print to stdout an attestator-compatible host file",
    )
    export_group.add_argument(
        EXPORT_AS_VSOCK_PROXY_SCRIPT,
        action="store_true",
        help="print to stdout a vsock proxy launcher script \
              that will correctly proxy the forwarder's requests",
    )
    parser.add_argument(
        "--allow-list-path",
        default="vsock-proxy-allowlist.yaml",
        help=f"path to the vsock proxy allow-list, only affects `{EXPORT_AS_VSOCK_PROXY_SCRIPT}`",
    )
    args = parser.parse_args()

    host = args.host if args.debug else args.cid
    forward_server = ForwardServer.from_config_toml(
        args.config, host, args.out_port, args.debug
    )

    if args.export_as_allow_list:
        print("allowlist:")
        for rpc in forward_server.rpc_map:
            print(f"- {{address: {rpc}, port: 443}}")
    elif args.export_as_hosts:
        for rpc in forward_server.rpc_map:
            print(f"127.0.0.1   {rpc}")
    elif args.export_as_vsock_proxy_script:
        print("#!/bin/bash")
        for rpc, port in forward_server.rpc_map.items():
            print(f"vsock-proxy --config {args.allow_list_path} {port} {rpc} 443 &")
    else:
        server = await asyncio.start_server(
            forward_server.run, host="0.0.0.0", port=args.port
        )

        await server.serve_forever()


if __name__ == "__main__":
    asyncio.run(main(sys.argv[1:]))
