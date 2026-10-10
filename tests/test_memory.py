
from mem0 import Memory


def test_memory_can_be_saved_and_retrieved():
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

    memory = Memory.from_config(config)
    user_id = "pytest_memory_test"

    fact = (
        "The project testing fact is that persistent memory "
        "should work across separate sessions."
    )

    memory.add(fact, user_id=user_id)

    result = memory.search(
        query="What should work across separate sessions?",
        filters={"user_id": user_id},
    )

    memories = result.get("results", [])
    assert memories, "No memories were retrieved"

    retrieved_text = " ".join(
        item.get("memory", "") for item in memories
    ).lower()

    assert (
        "persistent memory" in retrieved_text
        or "separate sessions" in retrieved_text
    ), f"Expected fact not found. Retrieved: {retrieved_text}"
