import unittest
from io import StringIO
from unittest.mock import patch

from autogpt.project.agent.config import AgentConfig
from autogpt.setup import (
    generate_aiconfig_automatic,
    generate_aiconfig_manual,
    prompt_user,
)
from tests.utils import requires_api_key


class TestAutoGPT(unittest.TestCase):
    @requires_api_key("OPENAI_API_KEY")
    def test_generate_aiconfig_automatic_default(self):
        user_inputs = [""]
        with patch("builtins.input", side_effect=user_inputs):
            agent_config = prompt_user()

        self.assertIsInstance(agent_config, AgentConfig)
        self.assertIsNotNone(agent_config.agent_name)
        self.assertIsNotNone(agent_config.agent_role)
        self.assertGreaterEqual(len(agent_config.agent_goals), 1)
        self.assertLessEqual(len(agent_config.agent_goals), 5)

    @requires_api_key("OPENAI_API_KEY")
    def test_generate_aiconfig_automatic_typical(self):
        user_prompt = "Help me create a rock opera about cybernetic giraffes"
        agent_config = generate_aiconfig_automatic(user_prompt)

        self.assertIsInstance(agent_config, AgentConfig)
        self.assertIsNotNone(agent_config.agent_name)
        self.assertIsNotNone(agent_config.agent_role)
        self.assertGreaterEqual(len(agent_config.agent_goals), 1)
        self.assertLessEqual(len(agent_config.agent_goals), 5)

    @requires_api_key("OPENAI_API_KEY")
    def test_generate_aiconfig_automatic_fallback(self):
        user_inputs = [
            "T&GF£OIBECC()!*",
            "Chef-GPT",
            "an AI designed to browse bake a cake.",
            "Purchase ingredients",
            "Bake a cake",
            "",
            "",
        ]
        with patch("builtins.input", side_effect=user_inputs):
            agent_config = prompt_user()

        self.assertIsInstance(agent_config, AgentConfig)
        self.assertEqual(agent_config.agent_name, "Chef-GPT")
        self.assertEqual(agent_config.agent_role, "an AI designed to browse bake a cake.")
        self.assertEqual(agent_config.agent_goals, ["Purchase ingredients", "Bake a cake"])

    @requires_api_key("OPENAI_API_KEY")
    def test_prompt_user_manual_mode(self):
        user_inputs = [
            "--manual",
            "Chef-GPT",
            "an AI designed to browse bake a cake.",
            "Purchase ingredients",
            "Bake a cake",
            "",
            "",
        ]
        with patch("builtins.input", side_effect=user_inputs):
            agent_config = prompt_user()

        self.assertIsInstance(agent_config, AgentConfig)
        self.assertEqual(agent_config.agent_name, "Chef-GPT")
        self.assertEqual(agent_config.agent_role, "an AI designed to browse bake a cake.")
        self.assertEqual(agent_config.agent_goals, ["Purchase ingredients", "Bake a cake"])


if __name__ == "__main__":
    unittest.main()
