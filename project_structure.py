from pathlib import Path

root = Path(".")

for path in sorted(root.rglob("*")):
    print(path)
