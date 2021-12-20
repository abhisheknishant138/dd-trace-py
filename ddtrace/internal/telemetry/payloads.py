from typing import Dict
from typing import List

from .data import create_dependency


def create_app_closed_payload():
    # type: () -> Dict
    "Creates payload of a TelemetryRequest which is sent after an application or process is terminated"
    return {}


def _get_app_dependencies():
    # type: () -> List[Dict]
    """returns a list of all package names and version in the working set of an applications"""
    import pkg_resources

    return [create_dependency(pkg.project_name, pkg.version) for pkg in pkg_resources.working_set]


def _get_app_configurations():
    # type: () -> Dict[str, str]
    """returns a map of all configured datadog enviornment vairables"""
    return {}


def create_app_started_payload():
    # type: () -> Dict
    """Creates payload of a TelemetryRequest which is sent at the start of the an application or process"""
    return {
        "dependencies": _get_app_dependencies(),
        "configurations": _get_app_configurations(),
    }


def create_integrations_changed_payload(integrations):
    # type: (List[Dict]) -> Dict
    """Creates payload of a TelemetryRequest which is sent after we attempt to instrument a module"""
    return {
        "integrations": integrations,
    }
