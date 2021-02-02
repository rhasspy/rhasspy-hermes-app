"""Tests for HermesApp arguments."""
# pylint: disable=no-member
import argparse

from rhasspyhermes_app import HermesApp


def test_default_arguments(mocker):
    """Test whether default arguments are set up correctly in a HermesApp object."""
    app = HermesApp("Test default arguments", mqtt_client=mocker.MagicMock())

    assert app.args.host == "localhost"
    assert app.args.port == 1883
    assert app.args.tls is False
    assert app.args.username is None
    assert app.args.password is None


def test_arguments_from_cli(mocker):
    """Test whether arguments from the command line are set up correctly in a HermesApp object."""
    mocker.patch(
        "sys.argv",
        [
            "rhasspy-hermes-app-test",
            "--host",
            "rhasspy.home",
            "--port",
            "8883",
            "--tls",
            "--username",
            "rhasspy-hermes-app",
            "--password",
            "test",
        ],
    )
    app = HermesApp("Test arguments in init", mqtt_client=mocker.MagicMock())

    assert app.args.host == "rhasspy.home"
    assert app.args.port == 8883
    assert app.args.tls is True
    assert app.args.username == "rhasspy-hermes-app"
    assert app.args.password == "test"


def test_arguments_in_init(mocker):
    """Test whether arguments are set up correctly while initializing a HermesApp object."""
    app = HermesApp(
        "Test arguments in init",
        mqtt_client=mocker.MagicMock(),
        host="rhasspy.home",
        port=8883,
        tls=True,
        username="rhasspy-hermes-app",
        password="test",
    )

    assert app.args.host == "rhasspy.home"
    assert app.args.port == 8883
    assert app.args.tls is True
    assert app.args.username == "rhasspy-hermes-app"
    assert app.args.password == "test"


def test_if_cli_arguments_overwrite_init_arguments(mocker):
    """Test whether arguments from the command line overwrite arguments to a HermesApp object."""
    mocker.patch(
        "sys.argv",
        [
            "rhasspy-hermes-app-test",
            "--host",
            "rhasspy.home",
            "--port",
            "1883",
            "--username",
            "rhasspy-hermes-app",
            "--password",
            "test",
        ],
    )
    app = HermesApp(
        "Test arguments in init",
        mqtt_client=mocker.MagicMock(),
        host="rhasspy.local",
        port=8883,
        username="rhasspy-hermes-app-test",
        password="covfefe",
    )

    assert app.args.host == "rhasspy.home"
    assert app.args.port == 1883
    assert app.args.username == "rhasspy-hermes-app"
    assert app.args.password == "test"


def test_if_cli_arguments_overwrite_init_arguments_with_argument_parser(mocker):
    """Test whether arguments from the command line overwrite arguments to a HermesApp object
    if the user supplies their own ArgumentParser object."""
    mocker.patch(
        "sys.argv",
        [
            "rhasspy-hermes-app-test",
            "--host",
            "rhasspy.home",
            "--port",
            "1883",
            "--username",
            "rhasspy-hermes-app",
            "--password",
            "test",
            "--test-argument",
            "foobar",
            "--test-flag",
        ],
    )
    parser = argparse.ArgumentParser(prog="rhasspy-hermes-app-test")
    parser.add_argument("--test-argument", default="foo")
    parser.add_argument("--test-flag", action="store_true")

    app = HermesApp(
        "Test arguments in init",
        parser=parser,
        mqtt_client=mocker.MagicMock(),
        host="rhasspy.local",
        port=8883,
        username="rhasspy-hermes-app-test",
        password="covfefe",
        test_argument="bar",
    )

    assert app.args.host == "rhasspy.home"
    assert app.args.port == 1883
    assert app.args.username == "rhasspy-hermes-app"
    assert app.args.password == "test"
    assert app.args.test_argument == "foobar"
    assert app.args.test_flag is True
