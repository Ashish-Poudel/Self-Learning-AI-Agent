
from mem0 import Memory

config = {
    "vector_store": {
        "provider": "qdrant",
        "config": {
            "collection_name": "self_learning_agent_test",
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

try:
    # Save a unique fact for User A.
    memory.add(
        "User A's private test fact is ORANGE-731.",
        user_id="isolation_user_a",
    )

    # Search using User B's ID.
    result = memory.search(
        query="What is the private test fact?",
        filters={"user_id": "isolation_user_b"},
    )

    memories = result.get("results", [])
    leaked = any(
        "ORANGE-731" in item.get("memory", "")
        for item in memories
    )

    if leaked:
        print("FAIL: User A's memory appeared in User B's results.")
    else:
        print("PASS: User A's memory was not returned to User B.")

finally:
    for store_name in ("vector_store", "_telemetry_vector_store"):
        store = getattr(memory, store_name, None)
        client = getattr(store, "client", None)

        if client is not None:
            client.close()
