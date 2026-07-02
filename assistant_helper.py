"""Helper function calling loop — alternatif Assistants API (L5)."""

import json
from typing import Any, Callable


def run_tool_calling_chat(
    client,
    model: str,
    user_message: str,
    tools: list[dict],
    available_functions: dict[str, Callable[..., Any]],
    max_rounds: int = 5,
) -> str:
    """Jalankan chat + function calling sampai model memberi jawaban final."""
    messages: list[dict[str, Any]] = [{"role": "user", "content": user_message}]

    for _ in range(max_rounds):
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            tools=tools,
            tool_choice="auto",
        )
        response_message = response.choices[0].message
        tool_calls = response_message.tool_calls

        if not tool_calls:
            return response_message.content or ""

        messages.append(response_message.model_dump())

        for tool_call in tool_calls:
            function_name = tool_call.function.name
            function_to_call = available_functions[function_name]
            function_args = json.loads(tool_call.function.arguments)
            function_response = function_to_call(**function_args)
            messages.append(
                {
                    "tool_call_id": tool_call.id,
                    "role": "tool",
                    "name": function_name,
                    "content": str(function_response),
                }
            )

    final = client.chat.completions.create(model=model, messages=messages)
    return final.choices[0].message.content or ""
