from __future__ import annotations

import logging
from importlib import import_module
from typing import List, Tuple

from autogpt.core.configuration import Configuration


class AgentFactory:
    configuration_defaults = {
        # Which subsystems to use. These must be subclasses of the base classes,
        # but could come from plugins.
        "system": {
            "budget_manager": "autogpt.core.budget.BudgetManager",
            "command_registry": "autogpt.core.command.CommandRegistry",
            "language_model": "autogpt.core.llm.LanguageModel",
            "memory_backend": "autogpt.core.memory.MemoryBackend",
            "planner": "autogpt.core.planning.Planner",
        }
    }

    def __init__(self, logger: logging.Logger):
        self._logger = logger

    def compile_configuration(
        self, user_configuration: dict
    ) -> Tuple[Configuration, List[str]]:
        """Compile the user's configuration with the defaults."""

        configuration_dict = self.configuration_defaults
        # Copy so we're not mutating the data structure we're looping over.
        system_defaults = self.configuration_defaults["system"].copy()
        # Build up default configuration
        for system_name in system_defaults:
            system_class = self.get_system_class(system_name, user_configuration)
            configuration_dict.update(system_class.configuration_defaults)

        # Apply user overrides
        configuration_dict.update(user_configuration)

        # TODO: Validate the user configuration and compile errors.
        agent_configuration = Configuration(configuration_dict)
        configuration_errors = []
        return agent_configuration, configuration_errors

    def get_system_class(self, system_name, configuration: dict | Configuration):
        """Get the system class for the given configuration."""
        if isinstance(configuration, Configuration):
            configuration = configuration.to_dict()

        default_system_import_path = self.configuration_defaults["system"][system_name]
        system_import_path = configuration["system"].get(
            system_name, default_system_import_path
        )

        module_path, _, class_name = system_import_path.rpartition(".")
        module = import_module(module_path)
        system_class = getattr(module, class_name)

        return system_class
