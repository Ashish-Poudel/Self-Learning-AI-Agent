
def test_memory_updates_changed_fact(memory):
    user_id = "memory_update_test_user"

    memory.add(
        "My favorite programming language is Python.",
        user_id=user_id,
    )

    memory.add(
        "My favorite programming language is Java. "
        "This replaces my previous preference for Python.",
        user_id=user_id,
    )

    result = memory.get_all(filters={"user_id": user_id})

    memories = [
        item.get("memory", "").lower()
        for item in result.get("results", [])
    ]

    print("\nStored memories:", memories)

    assert any("java" in item for item in memories), (
        f"Java was not saved. Stored memories: {memories}"
    )
