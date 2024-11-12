"""Hashing, signing and private key generation."""

from hashlib import sha256

from eth_account import Account


def generate_pk():
    """Return an `eth_account` `Account` with an appropriate private key."""
    # pylint: disable=no-value-for-parameter
    return Account.create()


def sha256_and_sign_with_key(message: bytes, key: Account):
    """Return hash and signature for `message` with the provided `key`."""
    hasher = sha256()
    hasher.update(message)
    message = hasher.digest()

    return message, key.unsafe_sign_hash(message)
