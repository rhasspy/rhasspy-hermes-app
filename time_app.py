from datetime import datetime
import logging

from rhasspyhermes_app import HermesApp

_LOGGER = logging.getLogger("TimeApp")

app = HermesApp("TimeApp")


@app.on_intent("GetTime")
def get_time(intent):
    now = datetime.now().strftime("%H %M")
    return app.EndSession(f"It's {now}")


app.run()
