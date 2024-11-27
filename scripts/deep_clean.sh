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

sudo systemctl stop docker
sudo rm -rf /var/lib/docker

cd $(dirname -- $0)/../

rm *.eif

cd -
