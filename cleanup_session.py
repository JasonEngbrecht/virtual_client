import os

files_deleted = []

# Delete the conversation service handoff file
if os.path.exists("conversation_service_handoff.md"):
    os.remove("conversation_service_handoff.md")
    files_deleted.append("conversation_service_handoff.md")

# Clean up temporary files
temp_files = [
    "check_conversation_tests.py",
    "test_conversation_quick.py", 
    "cleanup_temp.py",
    "final_cleanup.py",
    "cleanup_session.py"  # This file itself
]

for file in temp_files:
    if os.path.exists(file):
        if file != "cleanup_session.py":  # Don't delete while running
            os.remove(file)
            files_deleted.append(file)

print("Files deleted:")
for f in files_deleted:
    print(f"  - {f}")
print(f"\nTotal: {len(files_deleted)} files deleted")
print("\nNote: Delete cleanup_session.py manually after running")
