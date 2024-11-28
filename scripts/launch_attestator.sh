#!/bin/bash

set -e -u -o pipefail

scripts_path="$(realpath "$0")"
scripts_dir="$(dirname "$scripts_path")"
cd "$scripts_dir"/../

attestator="attestator"
eif_path="attestator.eif"

if [[ ! -v ATTESTATOR_CONFIG ]]; then
    echo "ATTESTATOR_CONFIG not set, exiting..."
    exit 1
fi

touch "$scripts_dir"/cert.pem
attestator_certs=""
if [[ -v ATTESTATOR_CERTS ]]; then
    attestator_certs="--build-arg ATTESTATOR_CERTS_ENABLED=true"
    if [[ -n $ATTESTATOR_CERTS ]]; then
        echo "ATTESTATOR_CERTS set, using $ATTESTATOR_CERTS..."
	attestator_certs="$attestator_certs --build-arg ATTESTATOR_CERTS=$ATTESTATOR_CERTS"
    else
        echo "ATTESTATOR_CERTS set, using $scripts_dir/cert.pem..."
    fi
else
    echo "ATTESTATOR_CERTS not set, using container defaults..."
fi

echo "Building attestator..."
docker build -t $attestator -f "$scripts_dir"/Dockerfile\
    --build-arg ATTESTATOR_CONFIG="$ATTESTATOR_CONFIG"\
    ${attestator_certs:+$attestator_certs} .

echo "Building enclave image..."
nitro-cli build-enclave --docker-uri $attestator --output-file $eif_path

echo "Terminating running attestators, if any..."
nitro-cli describe-enclaves | jq ".[] | select(.EnclaveName == \"$attestator\") | .EnclaveID" |\
    xargs -I{} nitro-cli terminate-enclave --enclave-id {}

echo "Writing vsock proxy script and configuration..."
docker run --rm attestator pipenv run python -m attestator.traffic_forwarder\
    --export-as-vsock-proxy-script ./config.toml > vsock_proxy.sh
chmod +x vsock_proxy.sh
docker run --rm attestator pipenv run python -m attestator.traffic_forwarder\
    --export-as-allow-list ./config.toml > vsock-proxy-allowlist.yaml

echo "Terminating running vsock proxies, if any..."
pkill vsock-proxy || true

echo "Starting vsock proxy script"
./vsock_proxy.sh

debug=""
if [[ -v DEBUG ]]; then
    echo "DEBUG set, starting attestator enclave in debug mode..."
    debug="--debug-mode"
else
    echo "DEBUG not set, starting attestator in normal mode..."
fi

echo "Cpu count: ${ATTESTATOR_CPU_COUNT:-2}"
echo "Cid: ${ATTESTATOR_CID:-100}"
echo "Memory: ${ATTESTATOR_MEMORY:-2048}"

nitro-cli run-enclave --eif-path $eif_path --cpu-count "${ATTESTATOR_CPU_COUNT:-2}"\
    --enclave-cid "${ATTESTATOR_CID:-100}" --memory "${ATTESTATOR_MEMORY:-2048}" $debug

cd -

if [[ -v DEBUG ]]; then
    nitro-cli describe-enclaves | jq "map(select(.EnclaveName == \"attestator\")) | .[0] | .EnclaveID" |\
        xargs -I{} nitro-cli console --enclave-id {}
fi
