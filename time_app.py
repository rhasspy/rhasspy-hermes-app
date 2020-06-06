"""Example app to react to an intent to tell you the time."""
import logging
from datetime import datetime

from rhasspyhermes.nlu import NluIntent

from rhasspyhermes_app import EndSession, HermesApp

_LOGGER = logging.getLogger("TimeApp")

app = HermesApp("TimeApp")


@app.on_intent("GetTime")
def get_time(intent: NluIntent):
    """Tell the time."""
    now = datetime.now().strftime("%H %M")
    return EndSession(f"It's {now}")


app.run()
