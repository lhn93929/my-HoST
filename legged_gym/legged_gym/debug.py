import sys
import os

print("Current working directory:", os.getcwd())
print("\nPython path:")
for p in sys.path:
    print("  ", p)

print("\nLooking for task_registry.py:")
for root, dirs, files in os.walk("/home/lhn"):
    if "task_registry.py" in files and "legged_gym" in root:
        print("Found at:", root)