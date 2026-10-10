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

memory = Memory.from_config(config)

result = memory.search(
    query="What is the persistence verification code?",
    filters={"user_id": "persistence_verification"},
)

memories = result.get("results", [])
print("Retrieved memories:", memories)

assert any(
    "BLUE-7319" in item.get("memory", "")
    for item in memories
), "The saved test memory was not retrieved."

print("PASS: Memory was retrieved in a separate Python process.")