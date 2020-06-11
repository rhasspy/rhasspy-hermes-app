"""Tests for rhasspyhermes_app intent."""
# pylint: disable=protected-access,too-many-function-args
import asyncio

import pytest
from rhasspyhermes.intent import Intent
from rhasspyhermes.nlu import NluIntent

from rhasspyhermes_app import HermesApp

INTENT_NAME = "GetTime"
INTENT_TOPIC = f"hermes/intent/{INTENT_NAME}"
INTENT = Intent(INTENT_NAME, 1.0)
NLU_INTENT = NluIntent("what time is it", INTENT)

INTENT_NAME2 = "GetTemperature"
INTENT_TOPIC2 = f"hermes/intent/{INTENT_NAME2}"
INTENT2 = Intent(INTENT_NAME2, 1.0)
NLU_INTENT2 = NluIntent("what's the temperature", INTENT2)

INTENT_NAME3 = "GetWeather"
INTENT_TOPIC3 = f"hermes/intent/{INTENT_NAME3}"
INTENT3 = Intent(INTENT_NAME3, 1.0)
NLU_INTENT3 = NluIntent("how's the weather", INTENT3)

_LOOP = asyncio.get_event_loop()


@pytest.mark.asyncio
async def test_callbacks_intent(mocker):
    """Test intent callbacks."""
    app = HermesApp("Test NluIntent", mqtt_client=mocker.MagicMock())

    # Mock intent callback and apply on_intent decorator.
    intent_handler = mocker.MagicMock()
    app.on_intent(INTENT_NAME)(intent_handler)

    intent_handler2 = mocker.MagicMock()
    app.on_intent(INTENT_NAME2, INTENT_NAME3)(intent_handler2)

    # Simulate app.run() without the MQTT client.
    app._subscribe_callbacks()

    # Simulate detected intent GetTime.
    await app.on_raw_message(INTENT_TOPIC, NLU_INTENT.to_json())
    # Check whether intent_handler has been called with the right Rhasspy Hermes object.
    intent_handler.assert_called_once_with(NLU_INTENT)
    intent_handler2.assert_not_called()

    # Simulate intent GetTemperature.
    intent_handler.reset_mock()
    intent_handler2.reset_mock()
    await app.on_raw_message(INTENT_TOPIC2, NLU_INTENT2.to_json())
    # Check whether intent_handler2 has been called with the right Rhasspy Hermes object.
    intent_handler2.assert_called_once_with(NLU_INTENT2)
    intent_handler.assert_not_called()

    # Simulate intent GetWeather.
    intent_handler.reset_mock()
    intent_handler2.reset_mock()
    # Check whether intent_handler2 has been called with the right Rhasspy Hermes object.
    await app.on_raw_message(INTENT_TOPIC3, NLU_INTENT3.to_json())
    intent_handler2.assert_called_once_with(NLU_INTENT3)
    intent_handler.assert_not_called()
