r"""
GoalieScout Path Handling Examples

This script demonstrates the correct way to handle file paths in Python,
especially addressing the common error with backslashes in Windows paths.

THE PROBLEM:
When you try to copy a Windows shell command like:
    cd Desktop\GoalieScout-copilot-check-past-projects
    
into Python code (which you should NOT do - this is a shell command, not Python!),
the backslash (\) is treated as an escape character.
Python sees \G and tries to interpret it as an escape sequence, which causes
an error because \G is not a valid escape sequence.

SOLUTIONS (for working with paths in Python):
"""

import os
from pathlib import Path

print("=" * 70)
print("GoalieScout - Python Path Handling Guide")
print("=" * 70)
print()

# Solution 1: Use raw strings (prefix with 'r')
print("Solution 1: Raw Strings")
print("-" * 70)
path1 = r"Desktop\GoalieScout-copilot-check-past-projects"
print(f"Raw string path: {path1}")
print("Code: path = r'Desktop\\GoalieScout-copilot-check-past-projects'")
print()

# Solution 2: Use forward slashes (works on Windows too!)
print("Solution 2: Forward Slashes (Cross-platform)")
print("-" * 70)
path2 = "Desktop/GoalieScout-copilot-check-past-projects"
print(f"Forward slash path: {path2}")
print("Code: path = 'Desktop/GoalieScout-copilot-check-past-projects'")
print()

# Solution 3: Escape the backslashes
print("Solution 3: Escaped Backslashes")
print("-" * 70)
path3 = "Desktop\\GoalieScout-copilot-check-past-projects"
print(f"Escaped backslash path: {path3}")
print("Code: path = 'Desktop\\\\GoalieScout-copilot-check-past-projects'")
print()

# Solution 4: Use pathlib (RECOMMENDED for modern Python)
print("Solution 4: Using pathlib.Path (RECOMMENDED)")
print("-" * 70)
path4 = Path("Desktop") / "GoalieScout-copilot-check-past-projects"
print(f"Path object: {path4}")
print("Code: path = Path('Desktop') / 'GoalieScout-copilot-check-past-projects'")
print()

# Solution 5: Use os.path.join
print("Solution 5: Using os.path.join")
print("-" * 70)
path5 = os.path.join("Desktop", "GoalieScout-copilot-check-past-projects")
print(f"os.path.join: {path5}")
print("Code: path = os.path.join('Desktop', 'GoalieScout-copilot-check-past-projects')")
print()

print("=" * 70)
print("IMPORTANT NOTES:")
print("=" * 70)
print("1. The 'cd' command is a SHELL command, not Python code.")
print("   Don't put shell commands directly in Python scripts.")
print()
print("2. To change directories in Python, use:")
print("   os.chdir(r'Desktop\\GoalieScout-copilot-check-past-projects')")
print("   or")
print("   os.chdir('Desktop/GoalieScout-copilot-check-past-projects')")
print()
print("3. The capital 'G' in 'Goalie' is fine - the problem is the backslash!")
print("   \\G is interpreted as an escape sequence (which doesn't exist).")
print()
print("=" * 70)
print("Example: Changing directory in Python")
print("=" * 70)
print()
print("# Instead of: cd Desktop\\GoalieScout-copilot-check-past-projects")
print("# Use this in Python:")
print()
print("import os")
print("os.chdir(r'Desktop\\GoalieScout-copilot-check-past-projects')")
print("# or")
print("os.chdir('Desktop/GoalieScout-copilot-check-past-projects')")
print()
