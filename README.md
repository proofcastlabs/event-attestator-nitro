# Event Attestator Nitro

This repository contains the core codebase for the Proofcast event attestation
system.

The purpose of the Event Attestator (EA) is to give its users the ability to prove,
on a destination blockchain B, that events or state changes have occurred on the
origin blockchain A, for any supported blockchain A and B. The proof is provided
as a Trusted Execution Environment (TEE)-backed signature of the event in question.

Currently the Event Attestator supports AWS' Nitro TEE.

## Attestator operation

The EA will provide a signature for any valid event available on the configured blockchains.
Only those events that match the signatures provided in the configuration file will
be signed.
Event data is provided to the EA through compatible rpc endpoints. Currently, these
are:

- `eth_getTransactionReceipt` for EVM-like blockchains.
- `v2/history/get_transaction` for Antelope blockchains.

The event data for a given event is considered reliable when *k of n* of the configured
endpoints agree on its content. Consensus might not be reached, tipically, if a
too-large number of endpoints are currently unreachable for a network request. In
that case, it's sufficient to try the event signing at a later time.

The rpc calls are secured via TLS. By default the EA will use Alpine's certificate
file. EA users can provide their own certificate file, see [configuration](#event-attestator-server-configuration).

## Project structure

- `attestation/`: rust binary crate that provides an interface to Nitro's NSM
- `attestator/`: core attestation logic and server-client architecture
- `scripts/`: bash scripts and Docker configurations necessary to run the attestator

## Running the Event Attestator

### Requirements

#### AWS' Nitro-enabled EC2 instance

todo!

#### `nitro-cli`

todo!

#### Docker

To install Docker follow the [instructions](https://docs.docker.com/engine/install/)
on the official documentation.

#### Git

To install git follow the [instructions](https://git-scm.com/downloads) on the
official documentation.

#### Python and Pipenv

Running the EA client requires a working installation of Python 3.12.7 and Pipenv.
If the correct python version is unavailable on your machine you can:

- Use `conda` through [miniconda](https://docs.anaconda.com/miniconda/install/),
following the [directions](https://docs.conda.io/projects/conda/en/latest/user-guide/tasks/manage-environments.html)
to create an environment that is Python 3.12.7 enabled.
- Download [Python 3.12.7](https://www.python.org/downloads/release/python-3127/)
and build it from source following the [build instructions](https://github.com/python/cpython/blob/3.12/README.rst#id4)
and the [developer guide](https://devguide.python.org/).

To install [Pipenv](https://pipenv.pypa.io/en/latest/) follow the
[instructions](https://pipenv.pypa.io/en/latest/installation.html) on the official
documentation.

### Event Attestator codebase

Clone the repository with `git clone https://github.com/proofcastlabs/event-attestator-nitro.git`

### Event Attestator Server configuration

The EA needs a toml configuration file that sets the following parameters, for each
supported blockchain:

- `endpoints`: list of rpc endpoints to be used for event data fetching and validation
- `consensus_threshold`: the *k* of the *n* configured endpoints that need to agree
on the event data for it to be considered valid. It's perfectly fine to set
`k = n` and not recommended to set `k < n/2 + 1`.
- `events`: list of filtered events. **Important**: only events that match the filter
for the configured blockchains will be signed. The event format is `[address, topic]`
for EVM events and `[accountName, action]` for EOS events.

See [server_config_example.toml](server_config_example.toml) for an example.

### Running the Event Attestator Server

The EA server can be started with the launcher script located at `scripts/launch_attestator.sh`
The following environment variables can be set to change the behavior of the launcher.

- `ATTESTATOR_CONFIG`: **required**, path to the configuration toml, needs to be
within the project directory tree
- `ATTESTATOR_CERTS`: if set but empty, use the cert file in `scripts/cert.pem`;
if set to path, use that instead; if unset, use Alpine's certificates. Defaults
to unset.
- `ATTESTATOR_CPU_COUNT`: available cpus, defaults to 2.
- `ATTESTATOR_CID`: server enclave's cid, defaults to 100. **Important**: this will
impact the ability of the client to connect to the server, if the same change is
not reflected in the client's configuration.
- `ATTESTATOR_MEMORY`: available memory, defaults to 2048.
- `DEBUG`: if set, start the server enclave in debug mode and connect to its console.
Defaults to unset.

Example invocation:

```bash
DEBUG= ATTESTATOR_CONFIG=./config.toml ./scripts/launch_attestator.sh
```
