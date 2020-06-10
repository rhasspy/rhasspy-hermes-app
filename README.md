# Rhasspy Hermes App library

[![Continous Integration](https://github.com/rhasspy/rhasspy-hermes-app/workflows/Tests/badge.svg)](https://github.com/rhasspy/rhasspy-hermes-app/actions)
[![Documentation Status](https://readthedocs.org/projects/rhasspy-hermes-app/badge/?version=latest)](https://rhasspy-hermes-app.readthedocs.io/en/latest/?badge=latest)
[![PyPI package version](https://img.shields.io/pypi/v/rhasspy-hermes-app.svg)](https://pypi.org/project/rhasspy-hermes-app)
[![Python versions](https://img.shields.io/pypi/pyversions/rhasspy-hermes-app.svg)](https://www.python.org)
[![GitHub license](https://img.shields.io/github/license/rhasspy/rhasspy-hermes-app.svg)](https://github.com/rhasspy/rhasspy-hermes-app/blob/master/LICENSE)

Helper library to create voice apps for [Rhasspy >=2.5](https://rhasspy.readthedocs.io/) in Python using the [Hermes protocol](https://docs.snips.ai/reference/hermes).

**Warning: Rhasspy Hermes App is currently alpha software, in a very early stage of its development. Anything may change at any time. The public API should not be considered stable. Consider this as a prototype.**

## Rationale

[Rhasspy Hermes](https://github.com/rhasspy/rhasspy-hermes/) is an extensive library implementing Hermes protocol support in Rhasspy. It implements a lot of the low-level details such as MQTT communication and converting JSON payloads and binary payloads to more usable Python classes. Thanks to the [HermesClient](https://github.com/rhasspy/rhasspy-hermes/blob/master/rhasspyhermes/client.py) class and the [cli](https://github.com/rhasspy/rhasspy-hermes/blob/master/rhasspyhermes/cli.py) module, you can easily implement a Rhasspy 'app'.

However, the result [still needs a lot of lines of code](time_app_direct.py). If you want to have control over the finer details of the Rhasspy Hermes library, this is fine. But if you just want to create a simple voice app that tells you the time, it should be easier. This is where the Rhasspy Hermes App library comes in. Its lets you write code such as [the following](time_app.py):

```python
from datetime import datetime
import logging

from rhasspyhermes_app import EndSession, HermesApp

_LOGGER = logging.getLogger("TimeApp")

app = HermesApp("TimeApp")


@app.on_intent("GetTime")
def get_time(intent):
    now = datetime.now().strftime("%H %M")
    return EndSession(f"It's {now}")


app.run()
```

Ignoring the import lines and the logger, what this code does is:

* creating a `HermesApp` object;
* defining a function `get_time` that ends a session by telling the time;
* running the app.

By applying the app's `on_intent` decorator to the function, this function will get executed when the app receives a "GetTime" intent.

In fact, the code [using Rhasspy Hermes directly](time_app_direct.py) and the one [using Rhasspy Hermes App](time_app.py) are doing exactly the same. Thanks to the extra abstraction layer of the Rhasspy Hermes App library, a few lines of code are enough to start a whole machinery behind the scenes.

Try the example app [time_app.py](time_app.py) with the `--help` flag to see what settings you can use to start the app (mostly connection settings for the MQTT broker):

```
python3 time_app.py --help
```

## Installation

You need Python 3.7 for Rhasspy Hermes App. For experimenting with and developing on the library, you should create a Python virtual environment with the `make venv` script (which also installs the dependencies) and activate it:

```shell
make venv
source .venv/bin/activate
```

After this, you can run the demo app `time_app.py` to try the library.

## Documentation

The documentation is still work in progress. You can generate the API documentation with:

```shell
make docs
```

After this, you can find the documentation in `docs/build/html`.

## TODO list

* Add decorators to react to other Hermes messages.
* Improve `mypy` coverage.
* Write `pytest` tests.
* Release an installable Python package on PyPI when the API has been stabilised.
* Let the app load its intents/slots/… from a file and re-train Rhasspy on installation/startup of the app.
* Make multi-language apps possible, so the app developer can define example sentences in multiple languages and the app uses the language from your Rhasspy setup's profile.

See also the repository's [issues](https://github.com/rhasspy/rhasspy-hermes-app/issues).

## License

This project is provided by [Koen Vervloesem](mailto:koen@vervloesem.eu) as open source software with the MIT license. See the LICENSE file for more information.
