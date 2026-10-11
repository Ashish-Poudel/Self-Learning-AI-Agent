
import json

from mem0 import Memory
from ollama import Client
from tools import calculate


# -----------------------------
# 1. Configure persistent memory
# -----------------------------

config = {
    "vector_store": {
        "provider": "qdrant",
        "config": {
            "collection_name": "self_learning_agent",
            "path": "./qdrant_data",
            "on_disk": True,
            "embedding_model_dims": 768,
        },
    },
    "llm": {
        "provider": "ollama",
        "config": {
            "model": "llama3.2:3b",
            "temperature": 0,
            "ollama_base_url": "http://localhost:11434",
        },
    },
    "embedder": {
        "provider": "ollama",
        "config": {
            "model": "nomic-embed-text",
            "ollama_base_url": "http://localhost:11434",
        },
    },
}

memory = None


def get_memory():
    global memory

    if memory is None:
        memory = Memory.from_config(config)

    return memory
client = Client(host="http://localhost:11434")

USER_ID = "aashish"
MODEL_NAME = "llama3.2:3b"


# -----------------------------
# 2. Define the calculator tool
# -----------------------------

def calculator_tool(expression: str) -> str:
    """Calculate a basic arithmetic expression."""
    try:
        return str(calculate(expression))
    except (ValueError, SyntaxError, ZeroDivisionError, OverflowError) as error:
        return f"Calculation error: {error}"


tools = [
    {
        "type": "function",
        "function": {
            "name": "calculator",
            "description": (
                "Calculate arithmetic expressions when accurate "
                "numerical computation is needed."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "expression": {
                        "type": "string",
                        "description": (
                            "Arithmetic expression, for example "
                            "'(25 + 15) * 2'."
                        ),
                    }
                },
                "required": ["expression"],
            },
        },
    }
]


# -----------------------------
# 3. Chat with memory and tools
# -----------------------------

def chat(question):
    memory = get_memory()
    # Retrieve relevant memories
    result = memory.search(
        query=question,
        filters={"user_id": USER_ID},
    )

    memories = result.get("results", [])
    memory_context = "\n".join(
        f"- {item['memory']}"
        for item in memories
        if item.get("memory")
    )

    if not memory_context:
        memory_context = "No relevant saved memories found."

    
  
    system_prompt = f"""
You are a helpful personal AI assistant with persistent memory.

Your Python application automatically saves each conversation
to persistent memory after you respond. You can use relevant
saved memories provided below to answer questions about the user.

When the user asks you to remember a personal fact, acknowledge
it naturally, for example: "I'll remember that your favorite
car is the Thar."

Do not claim that you cannot remember personal facts.

Use the calculator ONLY when the user explicitly asks for a
calculation or when arithmetic is genuinely needed to answer.
Never use it for remembering facts, retrieving memories,
greetings, or ordinary conversation.

Do not invent memories. If a fact is not in the saved memories,
say you do not know it yet.

Saved memories:
{memory_context}
"""



    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": question},
    ]

    # Let the model decide whether a tool is needed
    response = client.chat(
        model=MODEL_NAME,
        messages=messages,
        tools=tools,
    )

    # Handle tool calls

# Handle tool calls safely
    message = response["message"]
    tool_calls = message.get("tool_calls", [])

 
    if tool_calls:
        messages.append(message)

        for tool_call in tool_calls:
            function_name = tool_call["function"]["name"]
            arguments = tool_call["function"].get("arguments", {})

            if function_name == "calculator":
                expression = arguments.get("expression", "")

                if expression:
                    tool_result = calculator_tool(expression)
                    print(f"[Calculator used: {expression}]")
                else:
                    tool_result = "No arithmetic expression was provided."
            else:
                tool_result = "No valid tool was selected."

            messages.append(
                {
                    "role": "tool",
                    "name": function_name,
                    "content": str(tool_result),
                }
            )

        response = client.chat(
            model=MODEL_NAME,
            messages=messages,
        )


    answer = response["message"]["content"].strip()

    # Fallback if the model returns no normal answer
    if not answer or answer.startswith('{"name":'):
        response = client.chat(
            model=MODEL_NAME,
            messages=[
                {
                    "role": "system",
                    "content": system_prompt
                    + "\nRespond with normal, helpful text. "
                      "Do not output JSON unless explicitly requested.",
                },
                {"role": "user", "content": question},
            ],
        )
        answer = response["message"]["content"].strip()

    print(f"\nAgent: {answer}\n")


    # Save the exchange to persistent memory
    greetings = {
        "hi", "hello", "hey",
        "good morning", "good afternoon", "good evening"
    }

    if question.lower().strip() not in greetings:
        memory.add(
            [
                {"role": "user", "content": question},
                {"role": "assistant", "content": answer},
            ],
            user_id=USER_ID,
        )


# -----------------------------
# 4. Run the interactive agent
# -----------------------------

def main():
    print("Personal AI Agent")
    print("Local Llama + Mem0 + Qdrant + Calculator")
    print("Type 'exit' to stop.\n")

    while True:
        question = input("You: ").strip()

        if question.lower() == "exit":
            print("Agent: Goodbye!")
            break

        if not question:
            continue

        try:
            chat(question)
        except Exception as error:
            print(f"\nAn error occurred: {error}\n")


if __name__ == "__main__":
    main()
