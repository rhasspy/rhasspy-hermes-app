"""Example app using topic lists for receiving raw MQTT messages."""
import logging

from rhasspyhermes_app import HermesApp, TopicData

_LOGGER = logging.getLogger("RawTopicApp")

app = HermesApp("RawTopicApp")


@app.on_topic(
    "hermes/dialogueManager/sessionStarted",
    "hermes/hotword/{hotword}/detected",
    "hermes/tts/+",
    "hermes/+/{site_id}/playBytes/#",
)
async def test_topic1(data: TopicData, payload: bytes):
    """Receive MQTT messages for the subscribed topics."""
    if "hotword" in data.topic:
        _LOGGER.debug("topic: %s, hotword: %s", data.topic, data.data.get("hotword"))
    elif "playBytes" in data.topic:
        _LOGGER.debug("topic: %s, site_id: %s", data.topic, data.data.get("site_id"))
    else:
        _LOGGER.debug("topic: %s, payload: %s", data.topic, payload.decode("utf-8"))


app.run()
