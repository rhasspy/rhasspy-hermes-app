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

.. _`since last release`: https://github.com/rhasspy/rhasspy-hermes-app/compare/v0.1.0...HEAD

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

Security
========



*********************
`0.1.0`_ - 2020-06-14
*********************

.. _`0.1.0`: https://github.com/rhasspy/rhasspy-hermes-app/releases/tag/v0.1.0

Added
=====

- This is the first released version with decorators :meth:`rhasspyhermes_app.HermesApp.on_hotword`,
  :meth:`rhasspyhermes_app.HermesApp.on_intent`, :meth:`rhasspyhermes_app.HermesApp.on_intent_not_recognized`
  and :meth:`rhasspyhermes_app.HermesApp.on_topic`.
