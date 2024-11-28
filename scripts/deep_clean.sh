#!/bin/bash

set -e -u -o pipefail

function confirm {
  while true; do
    read -p "$* [y/n]: " yn
    case $yn in
      [Yy]*) return 0;;
      [Nn]*) echo "Aborted"; return  1;;
    esac
  done
}

confirm "WARNING! Make sure you absolutely know what you are doing. Proceed?"

nitro-cli describe-enclaves | jq ".[] | select(.EnclaveName == \"attestator\") | .EnclaveID" |\
    xargs -I{} nitro-cli terminate-enclave --enclave-id {}

pkill vsock-proxy || true

sudo systemctl stop docker
sudo rm -rf /var/lib/docker

cd "$(dirname -- "$0")"/../

rm ./*.eif vsock_proxy.sh vsock-proxy-allowlist.yaml 2>/dev/null || true

cd -
