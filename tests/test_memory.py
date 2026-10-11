
def test_memory_can_be_saved_and_retrieved(memory):
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
