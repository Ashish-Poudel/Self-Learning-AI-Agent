
# Our first simple memory system

memories = []

# Save information
memories.append("I am learning Python.")
memories.append("I prefer simple explanations.")

print("Saved memories:")
for memory in memories:
    print("-", memory)

# Search for a memory using a keyword
query = input("\nWhat do you want to remember? ").lower()

print("\nSearch results:")
found = False

for memory in memories:
    if query in memory.lower():
        print("-", memory)
        found = True

if not found:
    print("No matching memory found.")