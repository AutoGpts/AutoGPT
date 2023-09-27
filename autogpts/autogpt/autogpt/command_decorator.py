from __future__ import annotations

import functools
import inspect
from typing import TYPE_CHECKING, Any, Callable, Literal, Optional
from autogpt.core.utils.json_schema import JSONSchema

if TYPE_CHECKING:
    from autogpt.agents.base import BaseAgent
    from autogpt.config import Config

from autogpt.models.command import Command, CommandOutput, CommandParameter

# Unique identifier for auto-gpt commands
AUTO_GPT_COMMAND_IDENTIFIER = "auto_gpt_command"


def command(
    name: str,
    description: str,
    parameters: dict[str, JSONSchema],
    enabled: Literal[True] | Callable[[Config], bool] = True,
    disabled_reason: Optional[str] = None,
    aliases: list[str] = [],
    available: Literal[True] | Callable[[BaseAgent], bool] = True,
) -> Callable[..., CommandOutput]:
    """The command decorator is used to create Command objects from ordinary functions."""

    def decorator(func: Callable[..., CommandOutput]):
        typed_parameters = [
            CommandParameter(
                name=param_name,
                spec=spec,
            )
            for param_name, spec in parameters.items()
        ]
        cmd = Command(
            name=name,
            description=description,
            method=func,
            parameters=typed_parameters,
            enabled=enabled,
            disabled_reason=disabled_reason,
            aliases=aliases,
            available=available,
        )

        if inspect.iscoroutinefunction(func):
            @functools.wraps(func)
            async def wrapper(*args, **kwargs) -> Any:
                return await func(*args, **kwargs)
        else:
            @functools.wraps(func)
            def wrapper(*args, **kwargs) -> Any:
                return func(*args, **kwargs)

        setattr(wrapper, "command", cmd)
        setattr(wrapper, AUTO_GPT_COMMAND_IDENTIFIER, True)

        return wrapper

    return decorator
