import logging
import os
import unittest
from unittest.mock import patch
from opentelemetry.trace import set_tracer_provider
from opentelemetry.sdk.trace import TracerProvider


class TestOtelSetup(unittest.TestCase):
    def setUp(self):
        # Forcefully reset tracer provider for test isolation
        set_tracer_provider(TracerProvider())

        logging.getLogger("opentelemetry.trace").setLevel(logging.ERROR)

        os.environ["MONKDB_OTEL_ENABLED"] = "true"
        os.environ["MONKDB_OTEL_EXPORTER_OTLP_ENDPOINT"] = "http://fake-otel-endpoint:4318"
        os.environ["MONKDB_OTEL_SERVICE_NAME"] = "test-otel-service"

    def tearDown(self):
        os.environ["MONKDB_OTEL_ENABLED"] = "false"
        os.environ.pop("MONKDB_OTEL_AUTH_HEADER", None)

    @patch("mcp_monkdb.otel_setup.RequestsInstrumentor.instrument")
    @patch("mcp_monkdb.otel_setup.BatchSpanProcessor")
    @patch("mcp_monkdb.otel_setup.OTLPSpanExporter")
    def test_otel_configure_called(self,
                                   mock_exporter,
                                   mock_processor,
                                   mock_requests_instrument):
        from mcp_monkdb.otel_setup import configure_otel
        configure_otel()

        mock_exporter.assert_called_once()
        mock_processor.assert_called_once()
        mock_requests_instrument.assert_called_once()

    @patch("mcp_monkdb.otel_setup.RequestsInstrumentor.instrument")
    @patch("mcp_monkdb.otel_setup.BatchSpanProcessor")
    @patch("mcp_monkdb.otel_setup.OTLPSpanExporter")
    def test_otel_configure_with_auth_header(self,
                                             mock_exporter,
                                             mock_processor,
                                             mock_requests_instrument):
        os.environ["MONKDB_OTEL_AUTH_HEADER"] = "Authorization=Bearer test-token-123"
        from mcp_monkdb.otel_setup import configure_otel
        configure_otel()

        mock_exporter.assert_called_once_with(
            endpoint="http://fake-otel-endpoint:4318",
            headers={"Authorization": "Bearer test-token-123"}
        )

    def test_otel_disabled_does_nothing(self):
        os.environ["MONKDB_OTEL_ENABLED"] = "false"
        from mcp_monkdb.otel_setup import configure_otel

        try:
            configure_otel()
        except Exception as e:
            self.fail(f"configure_otel raised exception when disabled: {e}")


if __name__ == "__main__":
    unittest.main()
