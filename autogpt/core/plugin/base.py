import abc
import dataclasses
from enum import StrEnum
from typing import Type

from autogpt.core.budget import BudgetManager
from autogpt.core.command import Command, CommandRegistry
from autogpt.core.llm import LanguageModel
from autogpt.core.memory import MemoryBackend
from autogpt.core.planning import Planner

# Expand to other types as needed
PluginType = (
    Type[BudgetManager]
    | Type[Command]
    | Type[CommandRegistry]
    | Type[LanguageModel]
    | Type[MemoryBackend]
    | Type[Planner]
)

Plugin = (
    BudgetManager | Command | CommandRegistry | LanguageModel | MemoryBackend | Planner
)


class PluginStorageFormat(StrEnum):
    """Supported plugin storage formats.

    Plugins can be stored at one of these supported locations.

    """

    # AUTO = "auto"  # We'll try to determine the plugin load location
    # AUTOGPT_PLUGIN_REPO = "autogpt_plugin_repo"  # Grab them from our managed repo
    WORKSPACE = "workspace"  # Grab them from the workspace
    # OTHER_FILE_PATH = "other_file_path"  # Grab them from a file path
    INSTALLED_PACKAGE = "installed_package"  # Grab them from an installed package
    # PYPI = "pypi"  # Grab them from pypi
    # GITHUB = "github"  # Grab them from a github repo
    # AUTOGPT_PLUGIN_SERVICE = "autogpt_plugin_service"  # Grab them from a service


PluginStorageRoute = str
PluginStorageRoute.__doc__ = """A plugin storage route.

This is a string that specifies where to load a plugin from
(e.g. an import path or file path).

"""


@dataclasses.dataclass
class PluginLocation:
    """A plugin location.

    This is a combination of a plugin storage format and a plugin storage route.
    It is used by the PluginService to load plugins.

    """

    storage_format: PluginStorageFormat
    storage_route: PluginStorageRoute


@dataclasses.dataclass
class PluginMetadata:
    """Metadata about a plugin."""

    name: str
    description: str
    type: PluginType
    location: PluginLocation


class PluginService(abc.ABC):
    """Base class for plugin service.

    The plugin service should be stateless. This defines
    """

    @staticmethod
    @abc.abstractmethod
    def get_plugin(plugin_location: PluginLocation) -> PluginType:
        """Get a plugin from a plugin location."""
        ...

    ####################################
    # Low-level storage format loaders #
    ####################################
    @staticmethod
    @abc.abstractmethod
    def load_from_file_path(plugin_route: PluginStorageRoute) -> PluginType:
        """Load a plugin from a file path."""

        ...

    @staticmethod
    @abc.abstractmethod
    def load_from_import_path(plugin_route: PluginStorageRoute) -> PluginType:
        """Load a plugin from an import path."""
        ...

    @staticmethod
    @abc.abstractmethod
    def resolve_name_to_path(
        plugin_route: PluginStorageRoute, path_type: str
    ) -> PluginStorageRoute:
        """Resolve a plugin name to a plugin path."""
        ...

    #####################################
    # High-level storage format loaders #
    #####################################

    @staticmethod
    @abc.abstractmethod
    def load_from_workspace(plugin_route: PluginStorageRoute) -> PluginType:
        """Load a plugin from the workspace."""
        ...

    @staticmethod
    @abc.abstractmethod
    def load_from_installed_package(plugin_route: PluginStorageRoute) -> PluginType:
        """Load a plugin from an installed package."""
        ...
