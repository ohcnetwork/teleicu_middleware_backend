
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")

import django
import asyncio
import aiorun
import logging 


from hl7.mllp import start_hl7_server

logger = logging.getLogger(__name__)

django.setup(set_prefix=False)


async def start_mllp_server():
    from middleware.lab_analyzer import handler

    logger.info("Starting HL7 MLLP server on port 2577")

    try:
        async with await start_hl7_server(
            handler.process_hl7_messages, port=2577
        ) as hl7_server:
            await hl7_server.serve_forever()
    except asyncio.CancelledError:
        pass
    except Exception as e:
        logger.error(f"Error starting HL7 server: {e}")


if __name__ == "__main__":
    aiorun.run(start_mllp_server(), stop_on_unhandled_errors=True)
