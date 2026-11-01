"""
system_control/app_adapters package for KAMACHI 2.0.
Contains specialized application adapters (Office, Browsers, VS Code, Media).
"""

from .office_adapter import OfficeAdapter, get_office_adapter

__all__ = [
    "OfficeAdapter",
    "get_office_adapter",
]

