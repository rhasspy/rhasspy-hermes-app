import logging

from rhasspyhermes_app import HermesApp, TopicData

_LOGGER = logging.getLogger("RawTopicApp")

app = HermesApp("RawTopicApp")


@app.on_topic("hermes/dialogueManager/sessionStarted", "hermes/hotword/{hotword}/detected", "hermes/tts/+", "hermes/+/{site_id}/playBytes/#")
def test_topic1(data: TopicData, payload: bytes):
    if 'hotword' in data.topic:
        _LOGGER.debug(f"topic: {data.topic}, hotword: {data.data.get('hotword')}")
    elif 'playBytes' in data.topic:
        _LOGGER.debug(f"topic: {data.topic}, site_id: {data.data.get('site_id')}")
    else:
        _LOGGER.debug(f"topic: {data.topic}, payload: {payload.decode('utf-8')}")


app.run()
