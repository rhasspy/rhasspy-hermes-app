###########
Development
###########

You can find the code of Rhasspy Hermes App `on GitHub`_.

.. _`on GitHub`: https://github.com/rhasspy/rhasspy-hermes-app

***********************************
Set up your development environment
***********************************

Rhasspy Hermes App is actively seeking contributions. If you want to start developing, `fork`_ the repository, clone your fork and install the project's (development) dependencies in a Python virtual environment:

.. code-block:: shell

  git clone https://github.com/<your_username>/rhasspy-hermes-app.git
  cd rhasspy-hermes-app
  make venv
  source .venv/bin/activate

.. _`fork`: https://help.github.com/en/github/getting-started-with-github/fork-a-repo

**************
Run all checks
**************

A good start to check whether your development environment is set up correctly and whether the current code is in working condition is to run the unit tests:

.. code-block:: shell

  make test

They shouldn't fail. It's good practice to run the unit tests before and after you work on something.

You should also run some basic checks for code style issues:

.. code-block:: shell

  make check

This also does static type checking with mypy_.

.. _mypy: http://mypy-lang.org/

The documentation is generated with:

.. code-block:: shell

  make docs

This also checks all references in the documentation and the docstrings in the code. The generated documentation can be previewed in ``docs/build/html``.

*********************
Development practices
*********************

- Before starting significant work, please propose it and discuss it first on the `issue tracker`_ on GitHub.
  Other people may have suggestions, will want to collaborate and will wish to review your code.
- Please work on one piece of conceptual work at a time. Keep each narrative of work in a different branch.
- As much as possible, have each commit solve one problem.
- A commit must not leave the project in a non-functional state.
- Check your code (``make check``), run the unit tests (``make test``) and generate the documentation (``make docs``)
  before you create a commit. These three commands should all succeed. If there are errors, try to solve them. If ``make check``
  complains about bad formatting, a ``make reformat`` will reformat the code automatically.
- Treat code, tests and documentation as one. If you add functionality, document it in a docstring and add a test.
- Create a `pull request`_ from your fork.

.. _`issue tracker`: https://github.com/rhasspy/rhasspy-hermes-app/issues

.. _`pull request`: https://help.github.com/en/github/collaborating-with-issues-and-pull-requests/creating-a-pull-request-from-a-fork

********************
Development workflow
********************

If you want to start working on a specific feature or bug fix, this is an example workflow:

- `Synchronize your fork`_ with the upstream repository and update your fork on GitHub.
- Create a new branch: ``git checkout -b <nameofbranch>``.
- Create your changes, including tests and documentation.
- Run all checks: ``make check && make test && make docs``.
- Solve any issues the checks find and rerun all checks until there are no errors left.
- Add the changed files with ``git add <files>``.
- Commit your changes with ``git commit``.
- Push your changes to your fork on GitHub.
- Create a pull request from your fork.

.. _`Synchronize your fork`: https://help.github.com/en/github/collaborating-with-issues-and-pull-requests/syncing-a-fork

*****************
Things to work on
*****************

Have a look at the issues in the `issue tracker`_, especially the following categories:

- `help wanted`_: Issues that could use some extra help.
- `good first issue`_: Issues that are good for newcomers to the project.

.. _`help wanted`: https://github.com/rhasspy/rhasspy-hermes-app/issues?q=is%3Aissue+is%3Aopen+label%3A%22help+wanted%22

.. _`good first issue`: https://github.com/rhasspy/rhasspy-hermes-app/issues?q=is%3Aissue+is%3Aopen+label%3A%22good+first+issue%22

************************
License of contributions
************************

By submitting patches to this project, you agree to allow them to be redistributed under the project's :doc:`license` according to the normal forms and usages of the open-source community.

It is your responsibility to make sure you have all the necessary rights to contribute to the project.
