#####
Usage
#####

The design philosophy of Rhasspy Hermes App is:

- It should be easy to create a Rhasspy app with minimal boilerplate code.
- All Rhasspy Hermes App code should behave by default in a sensible way.

*********************
Reacting to an intent
*********************

This example app reacts to the default "GetTime" intent that comes with Rhasspy's installation by telling you the current time:

.. literalinclude:: ../examples/time_app.py

Ignoring the import lines and the logger, what this code does is:

* creating a :class:`rhasspyhermes_app.HermesApp` object;
* defining an async function ``get_time`` that ends a session by telling the time;
* running the app.

By applying the app's :meth:`rhasspyhermes_app.HermesApp.on_intent` decorator to the function, this function will be called whenever the app receives an intent with the name "GetTime".

Try the example app `time_app.py`_ with the ``--help`` flag to see what settings you can use to start the app (mostly connection settings for the MQTT broker):

.. command-output:: PYTHONPATH=. python3 examples/time_app.py --help
   :shell:
   :cwd: ..

.. _`time_app.py`: https://github.com/rhasspy/rhasspy-hermes-app/blob/master/examples/time_app.py

You can pass all the settings as keyword arguments inside the constructor as well:
``rhasspyhermes_app.HermesApp("ExampleApp", host="192.168.178.123", port=12183)``. Note that arguments passed on the
command line have precedence over arguments passed to the constructor.

*********************
Connecting to Rhasspy
*********************

In its default configuration, Rhasspy's internal MQTT broker listens on port 12183, so this is what you need to connect to, using command-line or constructor arguments - see previous section for details.

If you are using docker, you will need to add to add this port to your ``docker-compose.yml`` file:

.. code-block::

  services:
    rhasspy:
      ports:
        - "12101:12101"   # this is the port used for the web interface
        - "12183:12183"   # you need this to access Rhasspy's MQTT port

If you're using an external MQTT broker, you probably want port 1883.  This is what most MQTT brokers use, and is Rhasspy Hermes App's default port.

********************
Continuing a session
********************

An intent handler doesn't have to end a session. You can continue the session to ask the user for extra information or just for a confirmation. For example:

.. literalinclude:: ../examples/continue_session.py

The functions ``turn_off_light`` and ``turn_on_light`` triggered by the intents ``TurnOffLight`` and ``TurnOnLight``, respectively, each continue the current session by asking for confirmation. They set the ``custom_data`` argument to the name of the intent. This way the handler for the intent ``Yes`` can check whether the user confirmed the intent ``TurnOffLight`` or ``TurnOnLight``: the value of ``custom_data`` gets passed during a session. If the function ``yes`` sees that ``custom_data`` has another value, this means that the user has triggered the intent ``Yes`` without being in a session for ``TurnOffLight`` or ``TurnOnLight``.

Instead of ending the session with a message depending on ``custom_data``, you can use the same approach in home automation applications, for instance for asking for confirmation before opening or closing a relay.

Try the example app `continue_session.py`_.

.. _`continue_session.py`: https://github.com/rhasspy/rhasspy-hermes-app/blob/master/examples/continue_session.py

******************
Notifying the user
******************

Your app's voice actions aren't limited to replying in a session. At any time, your app can inform the user of something without expecting a response. An example:

.. literalinclude:: ../examples/time_app_notification.py

This example starts a timer that notifies the user every minute with the current time. This is done using the :meth:`rhasspyhermes_app.HermesApp.notify` method, which accepts a message and a site ID.

Try the example app `time_app_notification.py`_.

.. _`time_app_notification.py`: https://github.com/rhasspy/rhasspy-hermes-app/blob/master/examples/time_app_notification.py

*******
Asyncio
*******

Every function that you decorate with Rhasspy Hermes App should be defined with the ``async`` keyword. However, you don't have to use the async functionality.

For apps which are time intensive by e.g. using database queries or API calls, we recommend the use of asynchronous functions.
These allow your code to handle multiple requests at the same time and therefore cutting down on precious runtime.

Try the example app `async_advice_app.py`_.

.. _`async_advice_app.py`: https://github.com/rhasspy/rhasspy-hermes-app/blob/master/examples/async_advice_app.py


******************
Other example apps
******************

The GitHub repository has a couple of other example apps showing the library's functionality:

- `raw_topic_app.py`_
- `raw_topic_list_app.py`_

.. _`raw_topic_app.py`: https://github.com/rhasspy/rhasspy-hermes-app/blob/master/examples/raw_topic_app.py
.. _`raw_topic_list_app.py`: https://github.com/rhasspy/rhasspy-hermes-app/blob/master/examples/raw_topic_list_app.py

*******************************
Building an app on this library
*******************************

If the API of this library changes, your app possibly stops working when it updates to the newest release of Rhasspy Hermes App. Therefore, it’s best to define a specific version in your ``requirements.txt`` file, for instance:

.. code-block::

  rhasspy-hermes-app==1.0.0

This way your app keeps working when the Rhasspy Hermes App adds incompatible changes in a new version.

The project adheres to the `Semantic Versioning`_ specification with major, minor and patch version.

Given a version number major.minor.patch, this project increments the:

- major version when incompatible API changes are made;
- minor version when functionality is added in a backwards-compatible manner;
- patch version when backwards-compatible bug fixes are made.

.. _`Semantic Versioning`: https://semver.org

****************
More information
****************

More information about the usage of the Rhasspy Hermes App library can be found in the :doc:`api`.
