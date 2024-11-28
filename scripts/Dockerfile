FROM ubuntu:latest AS builder

RUN apt-get update && apt-get install gcc curl -y
RUN curl https://sh.rustup.rs -sSf | bash -s -- -y
ENV PATH="/root/.cargo/bin:${PATH}"
RUN rustup target install x86_64-unknown-linux-musl

COPY ./attestation attestation
WORKDIR /attestation
RUN cargo build --release --target=x86_64-unknown-linux-musl

FROM alpine:3.20.3

COPY --from=builder /attestation/target/x86_64-unknown-linux-musl/release/attestation .

RUN apk add --no-cache python3 py3-pip

RUN mkdir /venv/
RUN python -m venv /venv/
ENV PATH="/venv/bin:$PATH"
RUN pip install -U pip
RUN pip install pipenv

COPY ./Pipfile Pipfile
COPY ./Pipfile.lock Pipfile.lock
RUN pipenv install --ignore-pipfile

COPY ./attestator attestator
ARG ATTESTATOR_CONFIG
COPY ${ATTESTATOR_CONFIG:?} config.toml

COPY ./scripts/entrypoint.sh entrypoint.sh

ARG ATTESTATOR_CERTS=./scripts/cert.pem
ARG ATTESTATOR_CERTS_ENABLED=false
COPY $ATTESTATOR_CERTS cert.pem
ENV ATTESTATOR_CERTS_ENABLED=${ATTESTATOR_CERTS_ENABLED}

CMD [ "./entrypoint.sh" ]
