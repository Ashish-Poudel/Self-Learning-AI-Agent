from mem0 import Memory


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


def main():
    print("Initializing Mem0...")
    memory = Memory.from_config(config)

    try:
        print("Saving a memory...")
        result = memory.add(
            "I am a computer engineering student learning to build AI agents.",
            user_id="aashish",
        )
        print("Saved:", result)

        print("\nSearching memories...")
        results = memory.search(
            query="What am I studying, and what am I learning?",
            filters={"user_id": "aashish"},
        )
        print("Search results:", results)

        print("\nMem0 test completed.")

    finally:
        for store_name in ("vector_store", "_telemetry_vector_store"):
            store = getattr(memory, store_name, None)
            client = getattr(store, "client", None)
            if client is not None:
                client.close()


if __name__ == "__main__":
    main()