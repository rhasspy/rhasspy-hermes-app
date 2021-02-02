"""Helper library to create voice apps for Rhasspy using the Hermes protocol."""
import argparse
import asyncio
import logging
import re
from copy import deepcopy
from dataclasses import dataclass
from typing import Awaitable, Callable, Dict, List, Optional, Union

import paho.mqtt.client as mqtt
import rhasspyhermes.cli as hermes_cli
from rhasspyhermes.client import HermesClient
from rhasspyhermes.dialogue import (
    DialogueContinueSession,
    DialogueEndSession,
    DialogueIntentNotRecognized,
    DialogueNotification,
    DialogueStartSession,
)
from rhasspyhermes.nlu import NluIntent, NluIntentNotRecognized
from rhasspyhermes.wake import HotwordDetected

_LOGGER = logging.getLogger("HermesApp")


@dataclass
class ContinueSession:
    """Helper class to continue the current session.

    Attributes:
        text: The text the TTS should say to start this additional request of the session.
        intent_filter: A list of intents names to restrict the NLU resolution on the
            answer of this query.
        custom_data: An update to the session's custom data. If not provided, the custom data
            will stay the same.
        send_intent_not_recognized: Indicates whether the dialogue manager should handle non recognized
            intents by itself or send them for the client to handle.
    """

    custom_data: Optional[str] = None
    text: Optional[str] = None
    intent_filter: Optional[List[str]] = None
    send_intent_not_recognized: bool = False


@dataclass
class EndSession:
    """Helper class to end the current session.

    Attributes:
        text: The text the TTS should say to end the session.
        custom_data: An update to the session's custom data. If not provided, the custom data
            will stay the same.
    """

    text: Optional[str] = None
    custom_data: Optional[str] = None


@dataclass
class TopicData:
    """Helper class for topic subscription.

    Attributes:
        topic: The MQTT topic.
        data: A dictionary holding extracted data for the given placeholder.
    """

    topic: str
    data: Dict[str, str]


class HermesApp(HermesClient):
    """A Rhasspy app using the Hermes protocol.

    Attributes:
        args: Command-line arguments for the Hermes app.

    Example:

    .. literalinclude:: ../examples/time_app.py
    """

    def __init__(
        self,
        name: str,
        parser: Optional[argparse.ArgumentParser] = None,
        mqtt_client: Optional[mqtt.Client] = None,
        **kwargs
    ):
        """Initialize the Rhasspy Hermes app.

        Arguments:
            name: The name of this object.

            parser: An argument parser.
                If the argument is not specified, the object creates an
                argument parser itself.

            mqtt_client: An MQTT client. If the argument
                is not specified, the object creates an MQTT client itself.

            **kwargs: Other arguments. This supports the same arguments as the command-line
                arguments, such has ``host`` and ``port``. Arguments specified by the user
                on the command line have precedence over arguments passed as ``**kwargs``.
        """
        if parser is None:
            parser = argparse.ArgumentParser(prog=name)
        # Add default arguments
        hermes_cli.add_hermes_args(parser)

        # overwrite argument defaults inside parser with argparse.SUPPRESS
        # so arguments that are not provided get ignored
        suppress_parser = deepcopy(parser)
        for action in suppress_parser._actions:
            action.default = argparse.SUPPRESS

        supplied_args = vars(suppress_parser.parse_args())
        default_args = vars(parser.parse_args([]))

        # Command-line arguments take precedence over the arguments of the HermesApp.__init__
        args = {**default_args, **kwargs, **supplied_args}
        self.args = argparse.Namespace(**args)

        # Set up logging
        hermes_cli.setup_logging(self.args)
        _LOGGER.debug(self.args)

        # Create MQTT client
        if mqtt_client is None:
            mqtt_client = mqtt.Client()

        # Initialize HermesClient
        # pylint: disable=no-member
        super().__init__(name, mqtt_client, site_ids=self.args.site_id)

        self._callbacks_hotword: List[Callable[[HotwordDetected], Awaitable[None]]] = []

        self._callbacks_intent: Dict[
            str,
            List[Callable[[NluIntent], Awaitable[None]]],
        ] = {}

        self._callbacks_intent_not_recognized: List[
            Callable[[NluIntentNotRecognized], Awaitable[None]]
        ] = []

        self._callbacks_dialogue_intent_not_recognized: List[
            Callable[[DialogueIntentNotRecognized], Awaitable[None]]
        ] = []

        self._callbacks_topic: Dict[
            str, List[Callable[[TopicData, bytes], Awaitable[None]]]
        ] = {}

        self._callbacks_topic_regex: List[
            Callable[[TopicData, bytes], Awaitable[None]]
        ] = []

        self._additional_topic: List[str] = []

    def _subscribe_callbacks(self) -> None:
        # Remove duplicate intent names
        intent_names: List[str] = list(set(self._callbacks_intent.keys()))
        topics: List[str] = [
            NluIntent.topic(intent_name=intent_name) for intent_name in intent_names
        ]

        if self._callbacks_hotword:
            topics.append(HotwordDetected.topic())

        if self._callbacks_intent_not_recognized:
            topics.append(NluIntentNotRecognized.topic())

        if self._callbacks_dialogue_intent_not_recognized:
            topics.append(DialogueIntentNotRecognized.topic())

        topic_names: List[str] = list(set(self._callbacks_topic.keys()))
        topics.extend(topic_names)
        topics.extend(self._additional_topic)

        self.subscribe_topics(*topics)

    async def on_raw_message(self, topic: str, payload: bytes):
        """This method handles messages from the MQTT broker.

        Arguments:
            topic: The topic of the received MQTT message.

            payload: The payload of the received MQTT message.

        .. warning:: Don't override this method in your app. This is where all the magic happens in Rhasspy Hermes App.
        """
        try:
            if HotwordDetected.is_topic(topic):
                # hermes/hotword/<wakeword_id>/detected
                try:
                    hotword_detected = HotwordDetected.from_json(payload)
                    for function_h in self._callbacks_hotword:
                        await function_h(hotword_detected)
                except KeyError as key:
                    _LOGGER.error(
                        "Missing key %s in JSON payload for %s: %s", key, topic, payload
                    )
            elif NluIntent.is_topic(topic):
                # hermes/intent/<intent_name>
                try:
                    nlu_intent = NluIntent.from_json(payload)
                    intent_name = nlu_intent.intent.intent_name
                    if intent_name in self._callbacks_intent:
                        for function_i in self._callbacks_intent[intent_name]:
                            await function_i(nlu_intent)
                except KeyError as key:
                    _LOGGER.error(
                        "Missing key %s in JSON payload for %s: %s", key, topic, payload
                    )
            elif NluIntentNotRecognized.is_topic(topic):
                # hermes/nlu/intentNotRecognized
                try:
                    nlu_intent_not_recognized = NluIntentNotRecognized.from_json(
                        payload
                    )
                    for function_inr in self._callbacks_intent_not_recognized:
                        await function_inr(nlu_intent_not_recognized)
                except KeyError as key:
                    _LOGGER.error(
                        "Missing key %s in JSON payload for %s: %s", key, topic, payload
                    )
            elif DialogueIntentNotRecognized.is_topic(topic):
                # hermes/dialogueManager/intentNotRecognized
                try:
                    dialogue_intent_not_recognized = (
                        DialogueIntentNotRecognized.from_json(payload)
                    )
                    for function_dinr in self._callbacks_dialogue_intent_not_recognized:
                        await function_dinr(dialogue_intent_not_recognized)
                except KeyError as key:
                    _LOGGER.error(
                        "Missing key %s in JSON payload for %s: %s", key, topic, payload
                    )
            else:
                unexpected_topic = True
                if topic in self._callbacks_topic:
                    for function_1 in self._callbacks_topic[topic]:
                        await function_1(TopicData(topic, {}), payload)
                        unexpected_topic = False
                else:
                    for function_2 in self._callbacks_topic_regex:
                        if hasattr(function_2, "topic_extras"):
                            topic_extras = getattr(function_2, "topic_extras")
                            for pattern, named_positions in topic_extras:
                                if re.match(pattern, topic) is not None:
                                    data = TopicData(topic, {})
                                    parts = topic.split(sep="/")
                                    if named_positions is not None:
                                        for name, position in named_positions.items():
                                            data.data[name] = parts[position]

                                    await function_2(data, payload)
                                    unexpected_topic = False

                if unexpected_topic:
                    _LOGGER.warning("Unexpected topic: %s", topic)

        except Exception:
            _LOGGER.exception("on_raw_message")

    def on_hotword(
        self, function: Callable[[HotwordDetected], Awaitable[None]]
    ) -> Callable[[HotwordDetected], Awaitable[None]]:
        """Apply this decorator to a function that you want to act on a detected hotword.

        The decorated function has a :class:`rhasspyhermes.wake.HotwordDetected` object as an argument
        and doesn't have a return value.

        Example:

        .. code-block:: python

            @app.on_hotword
            async def wake(hotword: HotwordDetected):
                print(f"Hotword {hotword.model_id} detected on site {hotword.site_id}")

        If a hotword has been detected, the ``wake`` function is called with the ``hotword`` argument.
        This object holds information about the detected hotword.
        """

        self._callbacks_hotword.append(function)

        return function

    def on_intent(
        self, *intent_names: str
    ) -> Callable[
        [
            Callable[
                [NluIntent], Union[Awaitable[ContinueSession], Awaitable[EndSession]]
            ]
        ],
        Callable[[NluIntent], Awaitable[None]],
    ]:
        """Apply this decorator to a function that you want to act on a received intent.

        Arguments:
            intent_names: Names of the intents you want the function to act on.

        The decorated function has a :class:`rhasspyhermes.nlu.NluIntent` object as an argument
        and needs to return a :class:`ContinueSession` or :class:`EndSession` object.

        If the function returns a :class:`ContinueSession` object, the intent's session is continued after
        saying the supplied text. If the function returns a a :class:`EndSession` object, the intent's session
        is ended after saying the supplied text, or immediately when no text is supplied.

        Example:

        .. code-block:: python

            @app.on_intent("GetTime")
            async def get_time(intent: NluIntent):
                return EndSession("It's too late.")

        If the intent with name GetTime has been detected, the ``get_time`` function is called
        with the ``intent`` argument. This object holds information about the detected intent.
        """

        def wrapper(
            function: Callable[
                [NluIntent], Union[Awaitable[ContinueSession], Awaitable[EndSession]]
            ]
        ) -> Callable[[NluIntent], Awaitable[None]]:
            async def wrapped(intent: NluIntent) -> None:
                message = await function(intent)
                if isinstance(message, EndSession):
                    if intent.session_id is not None:
                        self.publish(
                            DialogueEndSession(
                                session_id=intent.session_id,
                                text=message.text,
                                custom_data=message.custom_data,
                            )
                        )
                    else:
                        _LOGGER.error(
                            "Cannot end session of intent without session ID."
                        )
                elif isinstance(message, ContinueSession):
                    if intent.session_id is not None:
                        self.publish(
                            DialogueContinueSession(
                                session_id=intent.session_id,
                                text=message.text,
                                intent_filter=message.intent_filter,
                                custom_data=message.custom_data,
                                send_intent_not_recognized=message.send_intent_not_recognized,
                            )
                        )
                    else:
                        _LOGGER.error(
                            "Cannot continue session of intent without session ID."
                        )

            for intent_name in intent_names:
                try:
                    self._callbacks_intent[intent_name].append(wrapped)
                except KeyError:
                    self._callbacks_intent[intent_name] = [wrapped]

            return wrapped

        return wrapper

    def on_intent_not_recognized(
        self,
        function: Callable[
            [NluIntentNotRecognized],
            Union[Awaitable[ContinueSession], Awaitable[EndSession], Awaitable[None]],
        ],
    ) -> Callable[[NluIntentNotRecognized], Awaitable[None]]:
        """Apply this decorator to a function that you want to act when the NLU system
        hasn't recognized an intent.

        The decorated function has a :class:`rhasspyhermes.nlu.NluIntentNotRecognized` object as an argument
        and can return a :class:`ContinueSession` or :class:`EndSession` object or have no return value.

        If the function returns a :class:`ContinueSession` object, the current session is continued after
        saying the supplied text. If the function returns a a :class:`EndSession` object, the current session
        is ended after saying the supplied text, or immediately when no text is supplied. If the function doesn't
        have a return value, nothing is changed to the session.

        Example:

        .. code-block:: python

            @app.on_intent_not_recognized
            async def not_understood(intent_not_recognized: NluIntentNotRecognized):
                print(f"Didn't understand \"{intent_not_recognized.input}\" on site {intent_not_recognized.site_id}")

        If an intent hasn't been recognized, the ``not_understood`` function is called
        with the ``intent_not_recognized`` argument. This object holds information about the not recognized intent.
        """

        async def wrapped(inr: NluIntentNotRecognized) -> None:
            message = await function(inr)
            if isinstance(message, EndSession):
                if inr.session_id is not None:
                    self.publish(
                        DialogueEndSession(
                            session_id=inr.session_id,
                            text=message.text,
                            custom_data=message.custom_data,
                        )
                    )
                else:
                    _LOGGER.error(
                        "Cannot end session of NLU intent not recognized message without session ID."
                    )
            elif isinstance(message, ContinueSession):
                if inr.session_id is not None:
                    self.publish(
                        DialogueContinueSession(
                            session_id=inr.session_id,
                            text=message.text,
                            intent_filter=message.intent_filter,
                            custom_data=message.custom_data,
                            send_intent_not_recognized=message.send_intent_not_recognized,
                        )
                    )
                else:
                    _LOGGER.error(
                        "Cannot continue session of NLU intent not recognized message without session ID."
                    )

        self._callbacks_intent_not_recognized.append(wrapped)

        return wrapped

    def on_dialogue_intent_not_recognized(
        self,
        function: Callable[
            [DialogueIntentNotRecognized],
            Union[Awaitable[ContinueSession], Awaitable[EndSession], Awaitable[None]],
        ],
    ) -> Callable[[DialogueIntentNotRecognized], Awaitable[None]]:
        """Apply this decorator to a function that you want to act when the dialogue manager
        failed to recognize an intent and you requested to notify you of this event with the
        `sendIntentNotRecognized` flag.

        The decorated function has a :class:`rhasspyhermes.dialogue.DialogueIntentNotRecognized` object as an argument
        and can return a :class:`ContinueSession` or :class:`EndSession` object or have no return value.

        If the function returns a :class:`ContinueSession` object, the current session is continued after
        saying the supplied text. If the function returns a a :class:`EndSession` object, the current session
        is ended after saying the supplied text, or immediately when no text is supplied. If the function doesn't
        have a return value, nothing is changed to the session.

        Example:

        .. code-block:: python

            @app.on_dialogue_intent_not_recognized
            async def not_understood(intent_not_recognized: DialogueIntentNotRecognized):
                print(f"Didn't understand \"{intent_not_recognized.input}\" on site {intent_not_recognized.site_id}")

        If an intent hasn't been recognized, the ``not_understood`` function is called
        with the ``intent_not_recognized`` argument. This object holds information about the not recognized intent.
        """

        async def wrapped(inr: DialogueIntentNotRecognized) -> None:
            message = await function(inr)
            if isinstance(message, EndSession):
                if inr.session_id is not None:
                    self.publish(
                        DialogueEndSession(
                            session_id=inr.session_id,
                            text=message.text,
                            custom_data=message.custom_data,
                        )
                    )
                else:
                    _LOGGER.error(
                        "Cannot end session of dialogue intent not recognized message without session ID."
                    )
            elif isinstance(message, ContinueSession):
                if inr.session_id is not None:
                    self.publish(
                        DialogueContinueSession(
                            session_id=inr.session_id,
                            text=message.text,
                            intent_filter=message.intent_filter,
                            custom_data=message.custom_data,
                            send_intent_not_recognized=message.send_intent_not_recognized,
                        )
                    )
                else:
                    _LOGGER.error(
                        "Cannot continue session of dialogue intent not recognized message without session ID."
                    )

        self._callbacks_dialogue_intent_not_recognized.append(wrapped)

        return wrapped

    def on_topic(self, *topic_names: str):
        """Apply this decorator to a function that you want to act on a received raw MQTT message.

        Arguments:
            topic_names: The MQTT topics you want the function to act on.

        The decorated function has a :class:`TopicData` and a :class:`bytes` object as its arguments.
        The former holds data about the topic and the latter about the payload of the MQTT message.

        Example:

        .. code-block:: python

            @app.on_topic("hermes/+/{site_id}/playBytes/#")
            async def test_topic1(data: TopicData, payload: bytes):
                _LOGGER.debug("topic: %s, site_id: %s", data.topic, data.data.get("site_id"))

        .. note:: The topic names can contain MQTT wildcards (`+` and `#`) or templates (`{foobar}`).
            In the latter case, the value of the named template is available in the decorated function
            as part of the :class:`TopicData` argument.
        """

        def wrapper(function):
            async def wrapped(data: TopicData, payload: bytes):
                await function(data, payload)

            replaced_topic_names = []

            for topic_name in topic_names:
                named_positions = {}
                parts = topic_name.split(sep="/")
                length = len(parts) - 1

                def placeholder_mapper(part):
                    i, token = tuple(part)
                    if token.startswith("{") and token.endswith("}"):
                        named_positions[token[1:-1]] = i
                        return "+"

                    return token

                parts = list(map(placeholder_mapper, enumerate(parts)))
                replaced_topic_name = "/".join(parts)

                def regex_mapper(part):
                    i, token = tuple(part)
                    value = token
                    if i == 0:
                        value = (
                            "^[^+#/]"
                            if token == "+"
                            else "[^/]+"
                            if length == 0 and token == "#"
                            else "^" + token
                        )
                    elif i < length:
                        value = "[^/]+" if token == "+" else token
                    elif i == length:
                        value = (
                            "[^/]+"
                            if token == "#"
                            else "[^/]+$"
                            if token == "+"
                            else token + "$"
                        )

                    return value

                pattern = "/".join(map(regex_mapper, enumerate(parts)))

                if topic_name == pattern[1:-1]:
                    try:
                        self._callbacks_topic[topic_name].append(wrapped)
                    except KeyError:
                        self._callbacks_topic[topic_name] = [wrapped]
                else:
                    replaced_topic_names.append(replaced_topic_name)
                    if not hasattr(wrapped, "topic_extras"):
                        wrapped.topic_extras = []
                    wrapped.topic_extras.append(
                        (
                            re.compile(pattern),
                            named_positions if len(named_positions) > 0 else None,
                        )
                    )

            if hasattr(wrapped, "topic_extras"):
                self._callbacks_topic_regex.append(wrapped)
                self._additional_topic.extend(replaced_topic_names)

            return wrapped

        return wrapper

    def run(self):
        """Run the app. This method:

        - subscribes to all MQTT topics for the functions you decorated;
        - connects to the MQTT broker;
        - starts the MQTT event loop and reacts to received MQTT messages.
        """
        # Subscribe to callbacks
        self._subscribe_callbacks()

        # Try to connect
        # pylint: disable=no-member
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

    def notify(self, text: str, site_id: str = "default"):
        """Send a dialogue notification.

        Use this to inform the user of something without expecting a response.

        Arguments:
            text: The text to say.
            site_id: The ID of the site where the text should be said.
        """
        notification = DialogueNotification(text)
        self.publish(DialogueStartSession(init=notification, site_id=site_id))
