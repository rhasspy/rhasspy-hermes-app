"""Tests for rhasspyhermes_app hotword."""
from rhasspyhermes.wake import HotwordDetected

from rhasspyhermes_app import HermesApp

# pylint: disable=protected-access


def test_callbacks_hotword(mocker):
    """Test hotword callbacks."""
    app = HermesApp("Test HotwordDetected", mqtt_client=mocker.MagicMock())

    @app.on_hotword
    # pylint: disable=unused-variable
    def wake(hotword: HotwordDetected):
        print(f"Hotword {hotword.model_id} detected on site {hotword.site_id}")

    app._subscribe_callbacks()

    assert len(app._callbacks_hotword) == 1
