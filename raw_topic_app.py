import logging

from rhasspyhermes_app import HermesApp, TopicData

_LOGGER = logging.getLogger("RawTopicApp")

app = HermesApp("RawTopicApp")


@app.on_topic("hermes/hotword/{hotword}/detected")
def test_topic1(data: TopicData, payload: bytes):
    _LOGGER.debug(f"topic1: {data.topic}, hotword: {data.custom_data.get('hotword')}, payload: {payload.decode('utf-8')}")


@app.on_topic("hermes/dialogueManager/sessionStarted")
def test_topic2(data: TopicData, payload: bytes):
    _LOGGER.debug(f"topic2: {data.topic}, payload: {payload.decode('utf-8')}")


@app.on_topic("hermes/tts/+")
def test_topic3(data: TopicData, payload: bytes):
    _LOGGER.debug(f"topic3: {data.topic}, payload: {payload.decode('utf-8')}")


@app.on_topic("hermes/+/{site_id}/playBytes/#")
def test_topic4(data: TopicData, payload: bytes):
    _LOGGER.debug(f"topic4: {data.topic}, site_id: {data.custom_data.get('site_id')}")


app.run()
