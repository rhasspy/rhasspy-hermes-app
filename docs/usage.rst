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

You can pass all the settings as keyword arguments inside the constructor aswell:
:meth:`rhasspyhermes_app.HermesApp("ExampleApp", host="192.168.178.123", port=12183)`. Note that arguments passed on the
command line have precedence over arguments passed to the constructor.

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
