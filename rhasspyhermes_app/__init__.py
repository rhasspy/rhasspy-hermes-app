"""Helper library to create voice apps for Rhasspy using the Hermes protocol."""
import argparse
import asyncio
import logging
import re
from dataclasses import dataclass
from typing import Callable, Dict, List, Optional, Union, Pattern

import paho.mqtt.client as mqtt
import rhasspyhermes.cli as hermes_cli
from rhasspyhermes.client import HermesClient
from rhasspyhermes.dialogue import DialogueContinueSession, DialogueEndSession
from rhasspyhermes.nlu import NluIntent

_LOGGER = logging.getLogger("HermesApp")


class HermesApp(HermesClient):
    """A Rhasspy app using the Hermes protocol."""

    def __init__(self, name: str, parser: argparse.ArgumentParser = None):
        """Initialize the Rhasspy Hermes app."""
        if parser is None:
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

        self._callbacks_intent: Dict[
            str,
            List[
                Callable[
                    [NluIntent], Union[HermesApp.ContinueSession, HermesApp.EndSession]
                ]
            ],
        ] = {}

        self._callbacks_topic: Dict[
            str,
            List[
                Callable[
                    [str, bytes], ()
                ]
            ],
        ] = {}

    def _subscribe_callbacks(self):
        # Remove duplicate intent names
        intent_names = list(set(self._callbacks_intent.keys()))
        topics = [
            NluIntent.topic(intent_name=intent_name) for intent_name in intent_names
        ]

        topic_names = list(set(self._callbacks_topic.keys()))
        for topic_name in topic_names:
            topics.append(topic_name)

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
                unexpected_topic = True
                for key, callback in self._callbacks_topic.items():
                    for function in callback:
                        if topic == key or (hasattr(function, 'topic_pattern') and re.match(getattr(function, 'topic_pattern'), topic) is not None):
                            function(topic, payload)
                            unexpected_topic = False

                if unexpected_topic:
                    _LOGGER.warning("Unexpected topic: %s", topic)

        except Exception:
            _LOGGER.exception("on_raw_message")

    def on_intent(self, intent_name: str):
        """Decorator for intent methods."""

        def wrapper(function):
            def wrapped(intent: NluIntent):
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

    def on_topic(self, topic_name: str, pattern: Pattern = None):
        """Decorator for raw topic methods."""

        def wrapper(function):
            def wrapped(topic: str, payload: bytes):
                function(topic, payload)

            try:
                self._callbacks_topic[topic_name].append(wrapped)
            except KeyError:
                self._callbacks_topic[topic_name] = [wrapped]

            if pattern is not None:
                wrapped.topic_pattern = pattern

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
        slot: Optional[str] = None
            Unused
        """

        custom_data: Optional[str] = None
        text: Optional[str] = None
        intent_filter: Optional[List[str]] = None
        send_intent_not_recognized: bool = False
        slot: Optional[str] = None

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

        text: Optional[str] = None
        custom_data: Optional[str] = None
