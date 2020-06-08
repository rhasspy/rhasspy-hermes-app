"""Tests for rhasspyhermes_app hotword."""
# pylint: disable=protected-access
import asyncio

import pytest
from rhasspyhermes.wake import HotwordDetected
from rhasspyhermes_app import HermesApp

HOTWORD_TOPIC = "hermes/hotword/test/detected"
HOTWORD_PAYLOAD = '{"modelId": "test_model.ppn", "modelVersion": "", "modelType": "personal", "currentSensitivity": 0.5, "siteId": "test_site", "sessionId": null, "sendAudioCaptured": null}'.encode()

_LOOP = asyncio.get_event_loop()


@pytest.mark.asyncio
async def test_callbacks_hotword(mocker):
    """Test hotword callbacks."""
    app = HermesApp("Test HotwordDetected", mqtt_client=mocker.MagicMock())

    wake = mocker.MagicMock()

    app.on_hotword(wake)

    app._subscribe_callbacks()

    assert len(app._callbacks_hotword) == 1

    await app.on_raw_message(HOTWORD_TOPIC, HOTWORD_PAYLOAD)

    wake.assert_called_once_with(HotwordDetected.from_json(HOTWORD_PAYLOAD))
