"""Tests for rhasspyhermes_app NLU."""
# pylint: disable=protected-access,too-many-function-args
import asyncio

import pytest
from rhasspyhermes.nlu import NluIntentNotRecognized

from rhasspyhermes_app import HermesApp

INR_TOPIC = "hermes/nlu/intentNotRecognized"
INR = NluIntentNotRecognized(input="covfefe")

_LOOP = asyncio.get_event_loop()


@pytest.mark.asyncio
async def test_callbacks_intent_not_recognized(mocker):
    """Test intent not recognized callbacks."""
    app = HermesApp("Test intentNotRecognized", mqtt_client=mocker.MagicMock())

    # Mock callback and apply on_intent_not_recognized decorator.
    inr = mocker.MagicMock()
    app.on_intent_not_recognized(inr)

    # Simulate app.run() without the MQTT client.
    app._subscribe_callbacks()

    # Simulate intent not recognized message.
    await app.on_raw_message(INR_TOPIC, INR.to_json())

    # Check whether callback has been called with the right Rhasspy Hermes object.
    inr.assert_called_once_with(INR)
