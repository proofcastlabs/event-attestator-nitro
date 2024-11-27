# Event Attestator Nitro

This repository contains the core codebase for the Proofcast event attestation
system.
The purpose of the Event Attestator (EA) is to give its users the ability to prove,
on a destination blockchain B, that events or state changes have occurred on the
origin blockchain A, for any supported blockchain A and B. The proof is provided
as a Trusted Execution Environment (TEE)-backed signature of the event in question.

Currently the Event Attestator supports AWS' Nitro TEE.

## Project structure

- `attestation/`: rust binary crate that provides an interface to Nitro's NSM
- `attestator/`: core attestation logic and server-client architecture
- `scripts`: bash scripts and Docker configurations necessary to run the attestator

## Running the event attestator

### Requirements

#### AWS' Nitro-enabled EC2 instance

todo!

#### `nitro-cli`

todo!

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
