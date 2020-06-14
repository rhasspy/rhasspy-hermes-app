Rationale
=========

`Rhasspy Hermes`_ is an extensive library implementing Hermes protocol support in Rhasspy. It implements a lot of the low-level details such as MQTT communication and converting JSON payloads and binary payloads to more usable Python classes. Thanks to the HermesClient_ class and the cli_ module, you can easily implement a Rhasspy 'app'.

.. _`Rhasspy Hermes`: https://github.com/rhasspy/rhasspy-hermes/

.. _HermesClient: https://github.com/rhasspy/rhasspy-hermes/blob/master/rhasspyhermes/client.py

.. _cli: https://github.com/rhasspy/rhasspy-hermes/blob/master/rhasspyhermes/cli.py

However, the result `still needs a lot of lines of code`_. If you want to have control over the finer details of the Rhasspy Hermes library, this is fine. But if you just want to create a simple voice app that tells you the time, it should be easier. This is where the Rhasspy Hermes App library comes in. Its lets you write code such as `the following`_:

.. _`still needs a lot of lines of code`: https://github.com/rhasspy/rhasspy-hermes-app/blob/master/time_app_direct.py

.. _`the following`: https://github.com/rhasspy/rhasspy-hermes-app/blob/master/time_app.py

.. literalinclude:: ../time_app.py

In fact, the code using Rhasspy Hermes directly and the one using Rhasspy Hermes App are doing exactly the same. Thanks to the extra abstraction layer of the Rhasspy Hermes App library, a few lines of code are enough to start a whole machinery behind the scenes.
