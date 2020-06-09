"""Example app using topic for receiving raw MQTT messages."""
import logging

from rhasspyhermes_app import HermesApp, TopicData

_LOGGER = logging.getLogger("RawTopicApp")

app = HermesApp("RawTopicApp")


@app.on_topic("hermes/hotword/{hotword}/detected")
def test_topic1(data: TopicData, payload: bytes):
    """Receive topic with template."""
    _LOGGER.debug(
        "topic1: %s, hotword: %s, payload: %s",
        data.topic,
        data.data.get("hotword"),
        payload.decode("utf-8"),
    )


@app.on_topic("hermes/dialogueManager/sessionStarted")
def test_topic2(data: TopicData, payload: bytes):
    """Receive verbatim topic."""
    _LOGGER.debug("topic2: %s, payload: %s", data.topic, payload.decode("utf-8"))


@app.on_topic("hermes/tts/+")
def test_topic3(data: TopicData, payload: bytes):
    """Receive topic with wildcard."""
    _LOGGER.debug("topic3: %s, payload: %s", data.topic, payload.decode("utf-8"))


@app.on_topic("hermes/+/{site_id}/playBytes/#")
def test_topic4(data: TopicData, payload: bytes):
    """Receive topic with wildcards and template."""
    _LOGGER.debug("topic4: %s, site_id: %s", data.topic, data.data.get("site_id"))


app.run()
