from ollama import Client

client = Client(host="http://localhost:11434")

tools = [
    {
        "type": "function",
        "function": {
            "name": "calculator",
            "description": "Calculate arithmetic expressions accurately.",
            "parameters": {
                "type": "object",
                "properties": {
                    "expression": {
                        "type": "string",
                        "description": "The arithmetic expression to calculate.",
                    }
                },
                "required": ["expression"],
            },
        },
    }
]


def test_model_selects_calculator_tool():
    response = client.chat(
        model="llama3.2:3b",
        messages=[
            {
                "role": "user",
                "content": (
                    "Use the calculator tool to calculate 125 * 8. "
                    "You must call the tool instead of calculating mentally."
                ),
            }
        ],
        tools=tools,
    )

    tool_calls = response["message"].get("tool_calls", [])

    assert tool_calls, "The model did not call any tool."
    assert tool_calls[0]["function"]["name"] == "calculator"

    expression = tool_calls[0]["function"]["arguments"]["expression"]
    assert expression == "125 * 8"
