
import pytest
from mem0 import Memory


@pytest.fixture(scope="session")
def memory(tmp_path_factory):
    config = {
        "vector_store": {
            "provider": "qdrant",
            "config": {
                "collection_name": "self_learning_agent_test",
                "path": str(tmp_path_factory.mktemp("qdrant_data")),
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

    instance = Memory.from_config(config)

    try:
        yield instance
    finally:
        for store_name in ("vector_store", "_telemetry_vector_store"):
            store = getattr(instance, store_name, None)
            client = getattr(store, "client", None)

            if client is not None:
                client.close()
