#!bin/sh

ifconfig lo 127.0.0.1 netmask 255.0.0.0 up

pipenv run python -m attestator.traffic_forwarder --export-as-hosts ./config.toml >> /etc/hosts

nohup pipenv run python -m attestator.traffic_forwarder ./config.toml &

pipenv run python -m attestator.attestator_server ./config.toml
