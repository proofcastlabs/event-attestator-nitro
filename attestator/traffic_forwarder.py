"""Traffic forwarding outside an enclave through the VSock.

Taken from: https://web.archive.org/web/20241122155109/https://raw.githubusercontent.com/provable-t\
hings/ptokens-nitro-pbtc-on-eth/3a65913253e7d3e415931786ba42c8307830c68c/docker-enclave/traffic-for\
warder.py
"""

import socket
import sys
import threading
import time


def server(local_port, remote_cid, remote_port):
    """Run server accepting on `local_port` and sending towards `remote_cid`:`remote_port`."""
    try:
        dock_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        dock_socket.bind(("", local_port))
        dock_socket.listen(5)

        while True:
            client_socket = dock_socket.accept()[0]

            server_socket = socket.socket(socket.AF_VSOCK, socket.SOCK_STREAM)
            server_socket.connect((remote_cid, remote_port))

            outgoing_thread = threading.Thread(
                target=forward, args=(client_socket, server_socket)
            )
            incoming_thread = threading.Thread(
                target=forward, args=(server_socket, client_socket)
            )

            outgoing_thread.start()
            incoming_thread.start()
    finally:
        new_thread = threading.Thread(
            target=server, args=(local_port, remote_cid, remote_port)
        )
        new_thread.start()


def forward(source, destination):
    """Forward traffic from `source` to `destination`."""
    string = " "
    while string:
        string = source.recv(1024)
        if string:
            destination.sendall(string)
        else:
            source.shutdown(socket.SHUT_RD)
            destination.shutdown(socket.SHUT_WR)


def main(args):
    """Run traffic forwarder."""
    local_port = int(args[0])
    remote_cid = int(args[1])
    remote_port = int(args[2])

    thread = threading.Thread(target=server, args=(local_port, remote_cid, remote_port))
    thread.start()

    while True:
        time.sleep(60)


if __name__ == "__main__":
    main(sys.argv[1:])
