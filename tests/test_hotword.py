"""Tests for rhasspyhermes_app hotword."""
# pylint: disable=protected-access,too-many-function-args
import asyncio

import pytest
from rhasspyhermes.wake import HotwordDetected

from rhasspyhermes_app import HermesApp

HOTWORD_TOPIC = "hermes/hotword/test/detected"
HOTWORD = HotwordDetected("test_model")
HOTWORD_TOPIC2 = "hermes/hotword/test2/detected"
HOTWORD2 = HotwordDetected("test_model2")

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

    # Simulate detected hotword.
    await app.on_raw_message(HOTWORD_TOPIC, HOTWORD.to_json())

    # Check whether callback has been called with the right Rhasspy Hermes object.
    wake.assert_called_once_with(HOTWORD)

    # Simulate another detected hotword.
    wake.reset_mock()
    await app.on_raw_message(HOTWORD_TOPIC2, HOTWORD2.to_json())

    # Check whether callback has been called with the right Rhasspy Hermes object.
    wake.assert_called_once_with(HOTWORD2)
