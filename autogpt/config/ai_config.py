# sourcery skip: do-not-use-staticmethod
"""
Maintain backward Compatibility
"""
#from __future__ import annotations

import os
import platform
from pathlib import Path
from typing import Any, Optional, Type

import distro
import yaml

from autogpt.prompts.generator import PromptGenerator
from autogpt.projects.agent_model import AgentModel


# Soon this will go in a folder where it remembers more stuff about the run(s)
SAVE_FILE = str(Path(os.getcwd()) / "ai_settings.yaml")


class AIConfig(AgentModel):  

    # def __init__(
    #     self,
    #     ai_name: str = "",
    #     ai_role: str = "",
    #     ai_goals: list | None = None,
    #     api_budget: float = 0.0,
    # ) -> None:
        
    #     """
    #     Initialize a class instance

    #     Parameters:
    #         ai_name (str): The name of the AI.
    #         ai_role (str): The description of the AI's role.
    #         ai_goals (list): The list of objectives the AI is supposed to complete.
    #         api_budget (float): The maximum dollar value for API calls (0.0 means infinite)
    #     Returns:
    #         None
    #     """
        
    #     if ai_goals is None:
    #         ai_goals = []
    #         self.ai_name = ai_name
    #         self.ai_role = ai_role
    #         self.ai_goals = ai_goals
    #         self.api_budget = api_budget
    #         self.prompt_generator = None
    #         self.command_registry = None

    #         super().__init__(ai_name = ai_name,
    #                         ai_role = ai_role,
    #                         ai_goals = ai_goals,
    #                         api_budget = api_budget
    #                         )
    
    def construct_full_prompt(
        self, prompt_generator: Optional[PromptGenerator] = None
    ) -> str:
        """
        Returns a prompt to the user with the class information in an organized fashion.

        Parameters:
            None

        Returns:
            full_prompt (str): A string containing the initial prompt for the user
              including the ai_name, ai_role, ai_goals, and api_budget.
        """

        prompt_start = (
            "Your decisions must always be made independently without"
            " seeking user assistance. Play to your strengths as an LLM and pursue"
            " simple strategies with no legal complications."
            ""
        )

        from autogpt.config import Config
        from autogpt.prompts.prompt import build_default_prompt_generator

        cfg = Config()
        if prompt_generator is None:
            prompt_generator = build_default_prompt_generator()
        prompt_generator.goals = self.ai_goals
        prompt_generator.name = self.ai_name
        prompt_generator.role = self.ai_role
        prompt_generator.command_registry = self.command_registry
        for plugin in cfg.plugins:
            if not plugin.can_handle_post_prompt():
                continue
            prompt_generator = plugin.post_prompt(prompt_generator)

        if cfg.execute_local_commands:
            # add OS info to prompt
            os_name = platform.system()
            os_info = (
                platform.platform(terse=True)
                if os_name != "Linux"
                else distro.name(pretty=True)
            )

            prompt_start += f"\nThe OS you are running on is: {os_info}"

        # Construct full prompt
        full_prompt = f"You are {prompt_generator.name}, {prompt_generator.role}\n{prompt_start}\n\nGOALS:\n\n"
        for i, goal in enumerate(self.ai_goals):
            full_prompt += f"{i+1}. {goal}\n"
        if self.api_budget > 0.0:
            full_prompt += f"\nIt takes money to let you run. Your API budget is ${self.api_budget:.3f}"
        self.prompt_generator = prompt_generator
        full_prompt += f"\n\n{prompt_generator.generate_prompt_string()}"
        return full_prompt
