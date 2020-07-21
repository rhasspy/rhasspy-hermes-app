"""Example app to react to an intent to tell you the time."""
import logging
import json
import aiohttp

from rhasspyhermes.nlu import NluIntent

from rhasspyhermes_app import EndSession, HermesApp

_LOGGER = logging.getLogger("AdviceApp")

app = HermesApp("AdviceApp")

"""
This is JUST an example!
None of the authors, contributors, administrators, or anyone else connected with Rhasspy_Hermes_App,
in any way whatsoever, can be responsible for your use of the api endpoint.
"""
URL = 'https://api.advicslip.com/advice'

#@app.on_intent("GetAdvice")
async def get_advice(intent: NluIntent):
    """Giving life advice."""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(URL) as response:
                data = await response.read()
                message = json.loads(data)
                return EndSession(str(message['slip']['advice']))
    except aiohttp.ClientConnectionError:
        _LOGGER.exception("No Connection could be established.")
    except:  # pylint: disable=W0702
        _LOGGER.exception("An Exception occured")
    return EndSession("Sadly i cannot connect to my spring my whisdom. Maybe try later again.")

app.run()