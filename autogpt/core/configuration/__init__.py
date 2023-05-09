"""The configuration encapsulates settings for all Agent subsystems."""
from autogpt.core.configuration.base import Configuration
from autogpt.core.status import ShortStatus, Status

status = Status(
    module_name=__name__,
    short_status=ShortStatus.INTERFACE_DONE,
    handoff_notes="Interface has been created. Next up is creating a basic implementation.",
)
