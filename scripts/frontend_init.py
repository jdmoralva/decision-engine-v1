import subprocess
from pathlib import Path

frontend_dir = Path("frontend")

subprocess.run(
    ["npm", "run", "dev"],
    cwd=frontend_dir,
    check=True,
    shell=True
)

