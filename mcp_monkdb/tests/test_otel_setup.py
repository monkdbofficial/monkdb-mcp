import os
import unittest
from unittest.mock import patch


class TestOtelSetup(unittest.TestCase):
    def setUp(self):
        os.environ["MONKDB_OTEL_ENABLED"] = "true"
        os.environ["MONKDB_OTEL_EXPORTER_OTLP_ENDPOINT"] = "http://fake-otel-endpoint:4318"
        os.environ["MONKDB_OTEL_SERVICE_NAME"] = "test-otel-service"

    def tearDown(self):
        os.environ["MONKDB_OTEL_ENABLED"] = "false"

    @patch("opentelemetry.instrumentation.requests.RequestsInstrumentor.instrument")
    @patch("opentelemetry.sdk.trace.export.BatchSpanProcessor")
    @patch("opentelemetry.exporter.otlp.proto.http.trace_exporter.OTLPSpanExporter")
    def test_otel_configure_called(self,
                                   mock_exporter,
                                   mock_processor,
                                   mock_requests_instrument):
        from mcp_monkdb.otel_setup import configure_otel
        configure_otel()

        mock_exporter.assert_called_once()
        mock_processor.assert_called_once()
        mock_requests_instrument.assert_called_once()

    def test_otel_disabled_does_nothing(self):
        os.environ["MONKDB_OTEL_ENABLED"] = "false"
        from mcp_monkdb.otel_setup import configure_otel

        # Should not raise or do anything
        try:
            configure_otel()
        except Exception as e:
            self.fail(f"configure_otel raised exception when disabled: {e}")


if __name__ == "__main__":
    unittest.main()
