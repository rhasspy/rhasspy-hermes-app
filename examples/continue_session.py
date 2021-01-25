"""Example app that shows how to continue a session."""
import logging

from rhasspyhermes.nlu import NluIntent

from rhasspyhermes_app import ContinueSession, EndSession, HermesApp

_LOGGER = logging.getLogger("ContinueApp")

app = HermesApp("ContinueApp")


@app.on_intent("Yes")
async def yes(intent: NluIntent):
    """The user confirms."""
    if intent.custom_data == "TurnOffLight":
        response = "OK, turning off the light"
    elif intent.custom_data == "TurnOnLight":
        response = "OK, turning on the light"
    else:
        response = "We can!"

    return EndSession(response)


@app.on_intent("No")
async def no(intent: NluIntent):
    """The user says no."""
    return EndSession()


@app.on_intent("TurnOffLight")
async def turn_off_light(intent: NluIntent):
    """The user asks to turn off the light."""
    return ContinueSession(
        text="Do you really want to turn off the light?", custom_data="TurnOffLight"
    )


@app.on_intent("TurnOnLight")
async def turn_on_light(intent: NluIntent):
    """The user asks to turn on the light."""
    return ContinueSession(
        text="Do you really want to turn on the light?", custom_data="TurnOnLight"
    )


app.run()
