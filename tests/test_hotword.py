"""Tests for rhasspyhermes_app hotword."""
# pylint: disable=protected-access
import asyncio

import pytest
from rhasspyhermes.wake import HotwordDetected

from rhasspyhermes_app import HermesApp

HOTWORD_TOPIC = "hermes/hotword/test/detected"
HOTWORD_PAYLOAD = '{"modelId": "test_model.ppn", "modelVersion": "", "modelType": "personal", "currentSensitivity": 0.5, "siteId": "test_site"}'

_LOOP = asyncio.get_event_loop()


@pytest.mark.asyncio
async def test_callbacks_hotword(mocker):
    """Test hotword callbacks."""
    app = HermesApp("Test HotwordDetected", mqtt_client=mocker.MagicMock())

    # Mock wake callback and apply on_hotword decorator.
    wake = mocker.MagicMock()
    app.on_hotword(wake)

    # Simulate app.run() without the MQTT client.
    app._subscribe_callbacks()

    # Check whether callback has been added to the app.
    assert len(app._callbacks_hotword) == 1
    assert app._callbacks_hotword[0] == wake

    # Simulate detected hotword.
    await app.on_raw_message(HOTWORD_TOPIC, HOTWORD_PAYLOAD)

    # Check whether callback has been called with the right Rhasspy Hermes object.
    wake.assert_called_once_with(HotwordDetected.from_json(HOTWORD_PAYLOAD))
