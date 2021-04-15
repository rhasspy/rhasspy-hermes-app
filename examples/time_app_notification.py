"""Example app to tell you the time every minute with a notification."""
import logging
from datetime import datetime
import threading

from rhasspyhermes_app import HermesApp

_LOGGER = logging.getLogger("TimeNotificationApp")
SECONDS = 60


def tell_time():
    """Tell the time with a notification."""
    now = datetime.now().strftime("%H %M")
    app.notify(f"It's {now}", "laptop")
    threading.Timer(SECONDS, tell_time).start()


app = HermesApp("TimeNotificationApp")
threading.Timer(SECONDS, tell_time).start()
app.run()
