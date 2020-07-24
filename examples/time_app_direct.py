"""Example app using Rhasspy Hermes directly."""
import argparse
import asyncio
import logging
import typing
from datetime import datetime

import paho.mqtt.client as mqtt
import rhasspyhermes.cli as hermes_cli
from rhasspyhermes.client import HermesClient
from rhasspyhermes.dialogue import DialogueEndSession
from rhasspyhermes.nlu import NluIntent

_LOGGER = logging.getLogger("TimeApp")


class TimeApp(HermesClient):
    """Tells the time."""

    def __init__(self, mqtt_client, site_ids: typing.Optional[typing.List[str]] = None):
        super().__init__("TimeApp", mqtt_client, site_ids=site_ids)

        self.subscribe_topics(NluIntent.topic(intent_name="GetTime"),)

    async def on_raw_message(self, topic: str, payload: bytes):
        """Received message from MQTT broker."""

        try:
            if NluIntent.is_topic(topic):
                # hermes/intent/<intent_name>
                nlu_intent = NluIntent.from_json(payload)
                if nlu_intent.intent.intent_name == "GetTime":
                    now = datetime.now().strftime("%H %M")
                    if nlu_intent.session_id is not None:
                        self.publish(
                            DialogueEndSession(
                                session_id=nlu_intent.session_id,
                                site_id=nlu_intent.site_id,
                                text=f"It's {now}",
                            )
                        )
                    else:
                        _LOGGER.error(
                            "Cannot end session of intent without session ID."
                        )
            else:
                _LOGGER.warning("Unexpected topic: %s", topic)

        except Exception:
            _LOGGER.exception("on_raw_message")


def main():
    """Main entry point."""
    # Parse command-line arguments
    parser = argparse.ArgumentParser(prog="TimeApp")
    hermes_cli.add_hermes_args(parser)

    args = parser.parse_args()

    # Add default MQTT arguments
    hermes_cli.setup_logging(args)
    _LOGGER.debug(args)

    # Create MQTT client
    mqtt_client = mqtt.Client()
    hermes_client = TimeApp(mqtt_client, site_ids=args.site_id)

    # Try to connect
    _LOGGER.debug("Connecting to %s:%s", args.host, args.port)
    hermes_cli.connect(mqtt_client, args)
    mqtt_client.loop_start()

    try:
        # Run main loop
        asyncio.run(hermes_client.handle_messages_async())
    except KeyboardInterrupt:
        pass
    finally:
        mqtt_client.loop_stop()


if __name__ == "__main__":
    main()
