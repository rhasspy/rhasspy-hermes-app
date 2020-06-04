"""Helper library to create voice apps for Rhasspy using the Hermes protocol."""
import argparse
import asyncio
import logging
import re
from dataclasses import dataclass
from typing import Callable, Dict, List, Optional, Union

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
                    [str, bytes], None
                ]
            ],
        ] = {}

        self._callbacks_topic_regex: List[
            Callable[
                [str, bytes], None
            ]
        ] = []

        self._additional_topic: List[str] = []

    def _subscribe_callbacks(self):
        # Remove duplicate intent names
        intent_names = list(set(self._callbacks_intent.keys()))
        topics = [
            NluIntent.topic(intent_name=intent_name) for intent_name in intent_names
        ]

        topic_names = list(set(self._callbacks_topic.keys()))
        topics.extend(topic_names)
        topics.extend(self._additional_topic)

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
                if topic in self._callbacks_topic:
                    for function in self._callbacks_topic[topic]:
                        function(TopicData(topic, {}), payload)
                        unexpected_topic = False
                else:
                    for function in self._callbacks_topic_regex:
                        # for function in callback:
                        if hasattr(function, 'topic_extras'):
                            topic_extras = getattr(function, 'topic_extras')
                            for pattern, named_positions in topic_extras:
                                if re.match(pattern, topic) is not None:
                                    data = TopicData(topic, {})
                                    parts = topic.split(sep='/')
                                    if named_positions is not None:
                                        for name, position in named_positions.items():
                                            data.data[name] = parts[position]

                                    function(data, payload)
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

    def on_topic(self, *topic_names: str):
        """Decorator for raw topic methods."""

        def wrapper(function):
            def wrapped(data: TopicData, payload: bytes):
                function(data, payload)

            replaced_topic_names = []

            for topic_name in topic_names:
                named_positions = {}
                parts = topic_name.split(sep='/')
                length = len(parts) - 1

                def placeholder_mapper(part):
                    i, token = tuple(part)
                    if token.startswith('{') and token.endswith('}'):
                        named_positions[token[1:-1]] = i
                        return '+'

                    return token

                parts = list(map(placeholder_mapper, enumerate(parts)))
                replaced_topic_name = '/'.join(parts)

                def regex_mapper(part):
                    i, token = tuple(part)
                    value = token
                    if i == 0:
                        value = '^[^+#/]' if token == '+' else '[^/]+' if length == 0 and token == '#' else '^' + token
                    elif i < length:
                        value = '[^/]+' if token == '+' else token
                    elif i == length:
                        value = '[^/]+' if token == '#' else '[^/]+$' if token == '+' else token + '$'

                    return value

                pattern = '/'.join(map(regex_mapper, enumerate(parts)))

                if topic_name == pattern[1:-1]:
                    try:
                        self._callbacks_topic[topic_name].append(wrapped)
                    except KeyError:
                        self._callbacks_topic[topic_name] = [wrapped]
                else:
                    replaced_topic_names.append(replaced_topic_name)
                    if not hasattr(wrapped, 'topic_extras'):
                        wrapped.topic_extras = []
                    wrapped.topic_extras.append((re.compile(pattern), named_positions if len(named_positions) > 0 else None))

            if hasattr(wrapped, 'topic_extras'):
                self._callbacks_topic_regex.append(wrapped)
                self._additional_topic.extend(replaced_topic_names)

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


@dataclass
class TopicData:
    """Helper class for topic subscription.

        Attributes
        ----------
        topic: str
            The topic
        data: Optional[Dict[str, str]] = None
            Holds extracted data for given placeholder
    """

    topic: str
    data: Optional[Dict[str, str]] = None
