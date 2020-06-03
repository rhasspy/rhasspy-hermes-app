import json
import logging
import re

from rhasspyhermes_app import HermesApp

_LOGGER = logging.getLogger("RawTopicApp")

app = HermesApp("RawTopicApp")


@app.on_topic("hermes/hotword/+/detected", re.compile(r"^hermes/hotword/([^/]+)/detected"))
def test_topic(topic: str, payload: bytes):
    content = json.loads(payload.decode('utf-8'))
    _LOGGER.debug(f"topic: {topic}, model: {content['modelId']}")


@app.on_topic("hermes/dialogueManager/sessionStarted")
def test_topic1(topic: str, payload: bytes):
    _LOGGER.debug(f"topic: {topic}, payload: {payload.decode('utf-8')}")


app.run()
