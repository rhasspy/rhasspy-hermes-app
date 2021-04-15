"""Example app to tell you the time every minute with a notification."""
import logging
import threading
from datetime import datetime

from rhasspyhermes_app import HermesApp

_LOGGER = logging.getLogger("TimeNotificationApp")
SECONDS = 60
SITE_ID = "default"


def tell_time():
    """Tell the time with a notification."""
    now = datetime.now().strftime("%H %M")
    app.notify(f"It's {now}", SITE_ID)
    threading.Timer(SECONDS, tell_time).start()


app = HermesApp("TimeNotificationApp")
threading.Timer(SECONDS, tell_time).start()
app.run()
