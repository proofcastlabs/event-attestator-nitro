#!/bin/bash

set -u -o pipefail

nitro-cli describe-enclaves | jq ".[] | select(.EnclaveName == \"attestator\") | .EnclaveID" |\
    xargs -I{} nitro-cli terminate-enclave --enclave-id {}

pkill vsock-proxy

docker rmi attestator 2>/dev/null

cd "$(dirname "$0")"/../

rm ./*.eif vsock_proxy.sh vsock-proxy-allowlist.yaml 2>/dev/null

cd - 1>/dev/null
