"""App views"""

import asyncio
import logging

from flask import current_app as app, request

from ..attestator_client.main import main as client_main
from ..messages import GET_ATTESTATION, SIGN_EVENT, SUCCESS_RESPONSE


def get_signed_event(req_json):
    """Return signed events to the root view."""
    try:
        chain_id, tx_id = req_json.get("params", [])[0:2]
    except ValueError:
        return 'missing argument, pass "params = [chain_id, tx_id]"', 400

    client_args = app.config["client"].split()

    try:
        response = asyncio.run(client_main(client_args + [SIGN_EVENT, chain_id, tx_id]))
        if response.response_type == SUCCESS_RESPONSE:
            return {"result": response.response}
    except Exception as exc:
        logger = logging.getLogger(__name__)
        logger.exception("signed event got exception %s", exc)

    return "something went wrong", 500


def get_signer_details():
    """Return signer details to the root view."""
    client_args = app.config["client"].split()

    try:
        response = asyncio.run(client_main(client_args + [GET_ATTESTATION]))
        if response.response_type == SUCCESS_RESPONSE:
            address, pub_k, attestation = response.response
            return {
                "result": {
                    "publicKey": pub_k,
                    "account": address,
                    "attestation": attestation,
                }
            }
    except Exception as exc:
        logger = logging.getLogger(__name__)
        logger.exception("signer details got exception %s", exc)

    return "something went wrong", 500


def root_view():
    """Root view."""
    req_json = request.json
    if (method := req_json.get("method", "")) == "getSignedEvent":
        return get_signed_event(req_json)

    if method == "getSignerDetails":
        return get_signer_details()

    return f'bad method: "{method}"', 400
