import json
from typing import Any, Dict, Union
from call_ai_function import call_ai_function
from config import Config
cfg = Config()

def fix_and_parse_json(json_str: str, try_to_fix_with_gpt: bool = True):
    """Fix and parse the given JSON string."""
    json_schema = """
    {
    "command": {
        "name": "command name",
        "args":{
            "arg name": "value"
        }
    },
    "thoughts":
    {
        "text": "thought",
        "reasoning": "reasoning",
        "plan": "- short bulleted\n- list that conveys\n- long-term plan",
        "criticism": "constructive self-criticism",
        "speak": "thoughts summary to say to user"
    }
}
"""


def fix_and_parse_json(
    json_str: str,
    try_to_fix_with_gpt: bool = True
) -> Union[str, Dict[Any, Any]]:
    try:
        json_str = json_str.replace('\t', '')
        return json.loads(json_str)
    except json.JSONDecodeError as _:  # noqa: F841
        json_str = correct_json(json_str)
        try:
          brace_index = json_str.index("{")
          json_str = json_str[brace_index:]
          last_brace_index = json_str.rindex("}")
          json_str = json_str[:last_brace_index+1]
          return json.loads(json_str)
        except Exception as e:
          if try_to_fix_with_gpt:
            print(f"Warning: Failed to parse AI output, attempting to fix.\n If you see this warning frequently, it's likely that your prompt is confusing the AI. Try changing it up slightly.")
            # Now try to fix this up using the ai_functions
            ai_fixed_json = fix_json(json_str, json_schema)
            if ai_fixed_json != "failed":
                return json.loads(ai_fixed_json)
            else:
              print(f"Failed to fix ai output, telling the AI.") # This allows the AI to react to the error message, which usually results in it correcting its ways.
              return json_str
          else:
            raise e
        
def fix_json(json_str: str, schema: str) -> str:
    # Try to fix the JSON using gpt:
    function_string = "def fix_json(json_str: str, schema:str=None) -> str:"
    args = [f"'''{json_str}'''", f"'''{schema}'''"]
    description_string = """Fixes the provided JSON string to make it parseable and fully complient with the provided schema.\n If an object or field specified in the schema isn't contained within the correct JSON, it is ommited.\n This function is brilliant at guessing when the format is incorrect."""

    # If it doesn't already start with a "`", add one:
    if not json_str.startswith("`"):
      json_str = "```json\n" + json_str + "\n```"
    result_string = call_ai_function(
        function_string, args, description_string, model=cfg.fast_llm_model
    )
    if cfg.debug_mode:
        print("------------ JSON FIX ATTEMPT ---------------")
        print(f"Original JSON: {json_str}")
        print("-----------")
        print(f"Fixed JSON: {result_string}")
        print("----------- END OF FIX ATTEMPT ----------------")

    try:
        json.loads(result_string)  # just check the validity
        return result_string
    except:  # noqa: E722
        # Get the call stack:
        # import traceback
        # call_stack = traceback.format_exc()
        # print(f"Failed to fix JSON: '{json_str}' "+call_stack)
        return "failed"
