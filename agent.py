
import json
import re

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
# 2. Calculator tool
# -----------------------------

def calculator_tool(expression: str) -> str:
    """Calculate an arithmetic expression."""
    try:
        return str(calculate(expression))
    except (
        ValueError,
        SyntaxError,
        ZeroDivisionError,
        OverflowError,
    ) as error:
        return f"Calculation error: {error}"


tools = [
    {
        "type": "function",
        "function": {
            "name": "calculator",
            "description": (
                "Use only for genuine numerical calculations. "
                "Never use for greetings, personal facts, "
                "memory questions, or ordinary conversation."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "expression": {
                        "type": "string",
                        "description": (
                            "A mathematical expression, such as "
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
# 3. Decide whether calculation is needed
# -----------------------------

def needs_calculator(question: str) -> bool:
    question = question.lower().strip()

    personal_phrases = [
        "my favorite",
        "my favourite",
        "my name",
        "who are you",
        "what do you remember",
        "what do you know about me",
        "do you remember",
        "remember that",
        "tell me about myself",
    ]

    if any(phrase in question for phrase in personal_phrases):
        return False

    calculation_phrases = [
        "calculate",
        "compute",
        "work out",
        "solve",
        "evaluate",
        "how much is",
        "square root",
        "percentage",
        "percent of",
        "multiplied by",
        "divided by",
        "plus",
        "minus",
        "times",
    ]

    if any(phrase in question for phrase in calculation_phrases):
        return True

    # Examples: 25 + 15, 25 * 15, 25 / 5, 25 - 15
    arithmetic_pattern = (
        r"\d+(?:\.\d+)?\s*"
        r"[\+\*/%\-]\s*"
        r"\d+(?:\.\d+)?"
    )

    if re.search(arithmetic_pattern, question):
        return True

    number_operations = [
        "double",
        "triple",
        "half of",
        "square of",
        "cube of",
    ]

    if (
        any(word in question for word in number_operations)
        and re.search(r"\d", question)
    ):
        return True

    return False


# -----------------------------
# 4. Chat with memory and tools
# -----------------------------

def chat(question):
    memory_store = get_memory()

    # Retrieve relevant saved memories
    result = memory_store.search(
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

Use the saved memories below to answer questions about the user.
Prioritize memories that state a personal fact over memories
that merely record the user asking a question.

When asked to remember a personal fact, acknowledge it naturally.
Do not invent personal facts. If a fact is not in memory,
say that you do not know it yet.

Use a calculator only when one is provided and arithmetic is
genuinely needed. Never use it for greetings, personal facts,
or memory retrieval.

When a calculator result is available, use its exact result.
Never change or invent a numerical result.

Respond with normal, helpful text, not JSON, unless requested.

Saved memories:
{memory_context}
"""

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": question},
    ]

    # Offer the calculator only for likely calculations
    if needs_calculator(question):
        response = client.chat(
            model=MODEL_NAME,
            messages=messages,
            tools=tools,
        )
    else:
        response = client.chat(
            model=MODEL_NAME,
            messages=messages,
        )

    message = response["message"]
    tool_calls = message.get("tool_calls", [])

    answer = ""

    # -----------------------------
    # Handle calculator tool calls
    # -----------------------------

    if tool_calls:
        messages.append(message)
        calculator_results = []

        for tool_call in tool_calls:
            function_name = tool_call["function"]["name"]
            arguments = tool_call["function"].get("arguments", {})

            # Ollama normally supplies a dictionary, but handle
            # JSON strings too.
            if isinstance(arguments, str):
                try:
                    arguments = json.loads(arguments)
                except json.JSONDecodeError:
                    arguments = {}

            if (
                function_name == "calculator"
                and needs_calculator(question)
            ):
                expression = arguments.get("expression", "")

                if expression:
                    tool_result = calculator_tool(expression)
                    print(f"[Calculator used: {expression}]")
                    calculator_results.append(tool_result)
                else:
                    tool_result = "No arithmetic expression was provided."
            else:
                tool_result = "Tool call not permitted for this question."

            messages.append(
                {
                    "role": "tool",
                    "name": function_name,
                    "content": str(tool_result),
                }
            )

        if calculator_results:
            # Use the real calculator output directly.
            # Do not ask the language model to calculate again.
            answer = "\n".join(calculator_results)

        else:
            # If no usable calculator result exists, ask the
            # model to produce a normal response.
            response = client.chat(
                model=MODEL_NAME,
                messages=messages,
                options={"temperature": 0},
            )
            answer = response["message"]["content"].strip()

    else:
        # IMPORTANT: This handles normal answers when no tool
        # is called, including personal-memory questions.
        answer = response["message"]["content"].strip()

    # -----------------------------
    # Fallback for empty responses
    # -----------------------------

    if not answer or answer.startswith('{"name":'):
        response = client.chat(
            model=MODEL_NAME,
            messages=[
                {
                    "role": "system",
                    "content": system_prompt
                    + "\nGive a normal, helpful text response.",
                },
                {"role": "user", "content": question},
            ],
            options={"temperature": 0},
        )

        answer = response["message"]["content"].strip()

    # -----------------------------
    # Display the answer
    # -----------------------------

    print(f"\nAgent: {answer}\n")

    # -----------------------------
    # Save conversation to memory
    # -----------------------------

    greetings = {
        "hi",
        "hello",
        "hey",
        "good morning",
        "good afternoon",
        "good evening",
    }

    if question.lower().strip() not in greetings and answer:
        memory_store.add(
            messages=[
                {"role": "user", "content": question},
                {"role": "assistant", "content": answer},
            ],
            user_id=USER_ID,
            infer=True,
        )

    return answer


# -----------------------------
# 5. Run the interactive agent
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
