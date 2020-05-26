"""Helper library to create voice apps for Rhasspy using the Hermes protocol."""
import argparse
import asyncio
import logging
import typing
from dataclasses import dataclass

import paho.mqtt.client as mqtt
import rhasspyhermes.cli as hermes_cli
from rhasspyhermes.client import HermesClient
from rhasspyhermes.dialogue import DialogueContinueSession, DialogueEndSession
from rhasspyhermes.nlu import NluIntent

_LOGGER = logging.getLogger("HermesApp")


class HermesApp(HermesClient):
    """A Rhasspy app using the Hermes protocol."""

    def __init__(self, name: str):
        """Initialize the Rhasspy Hermes app."""
        parser = argparse.ArgumentParser(prog=name)
        # Add default arguments
        hermes_cli.add_hermes_args(parser)

        # Parse command-line arguments
        self.args = parser.parse_args()

        # Set up logging
        hermes_cli.setup_logging(self.args)
        _LOGGER.debug(self.args)

        # Create MQTT client
        mqtt_client = mqtt.Client()

        # Initialize HermesClient
        super().__init__(name, mqtt_client, site_ids=self.args.site_id)

        self._callbacks_intent = {}

    def _subscribe_callbacks(self):
        # Remove duplicate intent names
        intent_names = list(set(self._callbacks_intent.keys()))
        topics = [
            NluIntent.topic(intent_name=intent_name) for intent_name in intent_names
        ]
        self.subscribe_topics(*topics)

    async def on_raw_message(self, topic: str, payload: bytes):
        """Received message from MQTT broker."""
        try:
            if NluIntent.is_topic(topic):
                # hermes/intent/<intent_name>
                nlu_intent = NluIntent.from_json(payload)
                intent_name = nlu_intent.intent.intent_name
                if intent_name in self._callbacks_intent:
                    for function in self._callbacks_intent[intent_name]:
                        function(nlu_intent)
            else:
                _LOGGER.warning("Unexpected topic: %s", topic)

        except Exception:
            _LOGGER.exception("on_raw_message")

    def on_intent(self, intent_name):
        """Decorator for intent methods."""

        def wrapper(function):
            def wrapped(intent):
                message = function(intent)
                if isinstance(message, self.EndSession):
                    self.publish(
                        DialogueEndSession(
                            session_id=intent.session_id,
                            site_id=intent.site_id,
                            text=message.text,
                            custom_data=message.custom_data,
                        )
                    )
                elif isinstance(message, self.ContinueSession):
                    self.publish(
                        DialogueContinueSession(
                            session_id=intent.session_id,
                            site_id=intent.site_id,
                            text=message.text,
                            intent_filter=message.intent_filter,
                            custom_data=message.custom_data,
                            send_intent_not_recognized=message.send_intent_not_recognized,
                            slot=message.slot,
                        )
                    )

            try:
                self._callbacks_intent[intent_name].append(wrapped)
            except KeyError:
                self._callbacks_intent[intent_name] = [wrapped]

            return wrapped

        return wrapper

    def run(self):
        """Run the app."""
        # Subscribe to callbacks
        self._subscribe_callbacks()

        # Try to connect
        _LOGGER.debug("Connecting to %s:%s", self.args.host, self.args.port)
        hermes_cli.connect(self.mqtt_client, self.args)
        self.mqtt_client.loop_start()

        try:
            # Run main loop
            asyncio.run(self.handle_messages_async())
        except KeyboardInterrupt:
            pass
        finally:
            self.mqtt_client.loop_stop()

    @dataclass
    class ContinueSession:
        """Helper class to continue the current session.

        Attributes
        ----------

        text: Optional[str] = None
            The text the TTS should say to start this additional request of the
            session.
        intent_filter: Optional[List[str]] = None
            A list of intents names to restrict the NLU resolution on the answer of
            this query.
        custom_data: Optional[str] = None
            An update to the session's custom data. If not provided, the custom data
            will stay the same.
        send_intent_not_recognized: bool = False
            Indicates whether the dialogue manager should handle non recognized
            intents by itself or send them for the client to handle.
        slot: typing.Optional[str] = None
            Unused
        """

        custom_data: typing.Optional[str] = None
        text: typing.Optional[str] = None
        intent_filter: typing.Optional[typing.List[str]] = None
        send_intent_not_recognized: bool = False
        slot: typing.Optional[str] = None

    @dataclass
    class EndSession:
        """Helper class to end the current session.

        Attributes
        ----------
        text: Optional[str] = None
            The text the TTS should say to end the session
        custom_data: Optional[str] = None
            An update to the session's custom data. If not provided, the custom data
            will stay the same.
        """

        text: typing.Optional[str] = None
        custom_data: typing.Optional[str] = None
