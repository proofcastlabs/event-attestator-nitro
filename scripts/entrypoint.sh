#!/bin/sh

ifconfig lo 127.0.0.1 netmask 255.0.0.0 up

if ! $ATTESTATOR_CERTS_ENABLED; then
  cat /etc/ssl/certs/ca-certificates.crt > cert.pem
fi

pipenv run python -m attestator.traffic_forwarder --export-as-hosts ./config.toml >> /etc/hosts

nohup pipenv run python -m attestator.traffic_forwarder ./config.toml &

pipenv run python -m attestator.attestator_server -c cert.pem ./config.toml
