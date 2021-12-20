import platform
import sys
from typing import Dict

from ddtrace.internal.compat import PY3
from ddtrace.internal.runtime.container import get_container_info
from ddtrace.settings import _config as config

from ...version import get_version
from ..hostname import get_hostname


def create_dependency(name, version):
    # type: (str, str) -> Dict[str, str]
    """Stores the name and versions of python modules"""
    return {
        "name": name,
        "version": version,
    }


def create_integration(name, version="", enabled=True, auto_enabled=True, compatible="", error=""):
    # type: (str, str, bool, bool, str, str) -> Dict
    """Creates an Integration Dict and sets default values"""
    return {
        "name": name,
        "version": version,
        "enabled": enabled,
        "auto_enabled": auto_enabled,
        "compatible": compatible,
        "error": error,
    }


def _format_version_info(vi):
    # type: (sys._version_info) -> str
    """
    Helper function private to this module
    Converts sys.version_info into a string with the format x.x.x
    """
    return "%d.%d.%d" % (vi.major, vi.minor, vi.micro)


def _get_container_id():
    # type: () -> str
    """
    Helper function private to this module
    Get ID from docker container
    """
    container_info = get_container_info()
    if container_info:
        return container_info.container_id or ""
    return ""


def _get_os_version():
    # type: () -> str
    """
    Helper function private to this module
    Returns the os version for applications running on Unix, Mac or Windows 32-bit
    """
    ver, _, _ = platform.mac_ver()
    if ver:
        return ver
    _, ver, _, _ = platform.win32_ver()
    if ver:
        return ver

    _, ver = platform.libc_ver()
    if ver:
        return ver

    return ""


def _get_host():
    # type: () -> Dict[str, str]
    """Creates a dictionary to store host data using the platform module"""
    return {
        "os": platform.platform(aliased=True, terse=True),
        "hostname": get_hostname(),
        "os_version": _get_os_version(),
        "kernel_name": platform.system(),
        "kernel_release": platform.release(),
        "kernel_version": platform.version(),
        "container_id": _get_container_id(),
    }


def _get_application():
    # type: () -> Dict[str, str]
    """Creates a dictionary to store application data using ddtrace configurations and the System-Specific module"""
    return {
        "service_name": config.service or "unnamed_python_service",
        "service_version": config.version or "",
        "env": config.env or "",
        "language_name": "python",
        "language_version": _format_version_info(sys.version_info),
        "tracer_version": get_version(),
        "runtime_name": platform.python_implementation(),
        "runtime_version": _format_version_info(sys.implementation.version) if PY3 else "",
    }


APPLICATION = _get_application()
HOST = _get_host()
