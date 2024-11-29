"""Attestator client entrypoint."""

import asyncio
import logging
import pprint
import sys

from .main import main


logging.basicConfig(level=logging.DEBUG)

ret = asyncio.run(main(sys.argv[1:]))

pprint.pp(ret)
