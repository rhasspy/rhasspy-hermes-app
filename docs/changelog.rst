#########
Changelog
#########

All notable changes to the Rhasspy Hermes App project are documented in this file.

The format is based on `Keep a Changelog`_, and this project adheres to the `Semantic Versioning`_ specification with major, minor and patch version.

Given a version number major.minor.patch this project increments the:

- major version when incompatible API changes are made;
- minor version when functionality is added in a backwards-compatible manner;
- patch version when backwards-compatible bug fixes are made.

.. _`Keep a Changelog`: https://keepachangelog.com/en/1.0.0/

.. _`Semantic Versioning`: https://semver.org

**********
Unreleased
**********

Commits `since last release`_:

.. _`since last release`: https://github.com/rhasspy/rhasspy-hermes-app/compare/v1.1.1...HEAD

Added
=====

Changed
=======

Deprecated
==========

Removed
=======

Fixed
=====

- Added missing ``await`` in :meth:`rhasspyhermes_app.HermesApp.on_raw_message`. Pull request `#89 <https://github.com/rhasspy/rhasspy-hermes-app/pull/89>`_ by `@H3adcra5h <https://github.com/H3adcra5h>`_.

Security
========

*********************
`1.1.1`_ - 2021-01-13
*********************

.. _`1.1.1`: https://github.com/rhasspy/rhasspy-hermes-app/releases/tag/v1.1.1

Changed
=======

- Updated dependencies. The most important one is the upgrade to rhasspy-hermes 0.5.0.

*********************
`1.1.0`_ - 2020-08-28
*********************

.. _`1.1.0`: https://github.com/rhasspy/rhasspy-hermes-app/releases/tag/v1.1.0

Changed
=======

- Command-line arguments can now also be passed as keyword arguments to the constructor of a :class:`rhasspyhermes_app.HermesApp` object. Note that arguments on the command line have precedence. Pull request `#37 <https://github.com/rhasspy/rhasspy-hermes-app/pull/37>`_ by `@JonahKr <https://github.com/JonahKr>`_ with help from `@maxbachmann <https://github.com/maxbachmann>`_.

*********************
`1.0.0`_ - 2020-07-26
*********************

.. _`1.0.0`: https://github.com/rhasspy/rhasspy-hermes-app/releases/tag/v1.0.0

Changed
=======

- All decorators of this library now only work with ``async`` functions. Pull request `#16 <https://github.com/rhasspy/rhasspy-hermes-app/pull/16>`_ by `@JonahKr <https://github.com/JonahKr>`_. Existing code should only add the ``async`` keyword before the function definition to keep the code valid. See :doc:`usage` for some examples.

*********************
`0.2.0`_ - 2020-07-19
*********************

.. _`0.2.0`: https://github.com/rhasspy/rhasspy-hermes-app/releases/tag/v0.2.0

Added
=====

- Method :meth:`rhasspyhermes_app.HermesApp.notify` to send a dialogue notification. See `#10 <https://github.com/rhasspy/rhasspy-hermes-app/issues/10>`_.
- Decorator :meth:`rhasspyhermes_app.HermesApp.on_dialogue_intent_not_recognized` to act when the dialogue manager failed to recognize an intent. See `#9 <https://github.com/rhasspy/rhasspy-hermes-app/issues/9>`_.

*********************
`0.1.0`_ - 2020-06-14
*********************

.. _`0.1.0`: https://github.com/rhasspy/rhasspy-hermes-app/releases/tag/v0.1.0

Added
=====

- This is the first released version with decorators :meth:`rhasspyhermes_app.HermesApp.on_hotword`,
  :meth:`rhasspyhermes_app.HermesApp.on_intent`, :meth:`rhasspyhermes_app.HermesApp.on_intent_not_recognized`
  and :meth:`rhasspyhermes_app.HermesApp.on_topic`.
