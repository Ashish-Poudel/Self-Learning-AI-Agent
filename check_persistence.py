
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
    result = memory.search(
        query="What is my persistence test fact?",
        filters={"user_id": "persistence_test_user"},
    )

    memories = result.get("results", [])

    print("\nRetrieved memories:")

    if memories:
        for item in memories:
            print("-", item.get("memory", ""))
    else:
        print("No memories found.")

finally:
    # Close Qdrant clients before Python shuts down.
    for store_name in ("vector_store", "_telemetry_vector_store"):
        store = getattr(memory, store_name, None)
        client = getattr(store, "client", None)

        if client is not None:
            client.close()
