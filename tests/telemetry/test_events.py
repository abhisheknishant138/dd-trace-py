import mock

from ddtrace.internal.telemetry.data import create_dependency
from ddtrace.internal.telemetry.data import create_integration
from ddtrace.internal.telemetry.payloads import create_app_closed_payload
from ddtrace.internal.telemetry.payloads import create_app_started_payload
from ddtrace.internal.telemetry.payloads import create_integrations_changed_payload


def test_app_started_payload():
    """validates the fields of AppStartedPayload typed dict"""

    with mock.patch("ddtrace.internal.telemetry.payloads._get_app_dependencies") as _get_app_dependencies:
        dependencies = [create_dependency("dependency", "0.0.0"), create_dependency("dependency2", "0.1.0")]
        _get_app_dependencies.return_value = dependencies
        with mock.patch("ddtrace.internal.telemetry.payloads._get_app_configurations") as _get_app_configurations:
            configurations = {"DD_PARTIAL_FLUSHING_ENABLED": True}
            _get_app_configurations.return_value = configurations

            asp = create_app_started_payload()
            assert asp == {"dependencies": dependencies, "configurations": configurations}


def test_app_closed_payload():
    """validates the fields of AppClosedPayload typed dict"""

    ace = create_app_closed_payload()
    assert ace == {}


def test_app_integrations_changed_payload():
    """validates the fields of AppIntegrationsChangedPayload typed dict"""

    integrations = [create_integration("integration-1"), create_integration("integration-2")]
    ace = create_integrations_changed_payload(integrations)
    assert ace == {"integrations": integrations}
