#!/bin/bash

set -u -o pipefail

scripts_dir=$(dirname -- $0)
cd $scripts_dir/../

attestator="attestator"
eif_path="attestator.eif"

if [[ ! -v ATTESTATOR_CONFIG ]]; then
  echo "ATTESTATOR_CONFIG not set, exiting..."
  exit 1
fi

echo "Building attestator..."
docker build -t $attestator -f $scripts_dir/Dockerfile --build-arg ATTESTATOR_CONFIG=$ATTESTATOR_CONFIG .
if (( $? )); then
  echo "Could not build attestator, exiting..."
  exit 1
fi

echo "Building enclave image..."
nitro-cli build-enclave --docker-uri $attestator --output-file $eif_path
if (( $? )); then
  echo "Could not build enclave image, exiting..."
  exit 1
fi

echo "Terminating running attestators, if any..."
nitro-cli describe-enclaves | jq ".[] | select(.EnclaveName == \"$attestator\") | .EnclaveID" | xargs -I{} nitro-cli terminate-enclave --enclave-id {}

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

nitro-cli run-enclave --eif-path $eif_path --cpu-count ${ATTESTATOR_CPU_COUNT:-2} --enclave-cid ${ATTESTATOR_CID:-100} --memory ${ATTESTATOR_MEMORY:-2048} $debug
if (( $? )); then
  echo "Could not start attestator, exiting..."
fi

cd -

if [[ -v DEBUG ]]; then
  nitro-cli describe-enclaves | jq "map(select(.EnclaveName == \"attestator\")) | .[0] | .EnclaveID" | xargs -I{} nitro-cli console --enclave-id {}
fi
