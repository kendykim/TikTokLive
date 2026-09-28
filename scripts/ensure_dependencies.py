"""Install only project dependencies that are missing from the active Python."""

import ast
import importlib.metadata
import re
import subprocess
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
PYPROJECT_PATH = PROJECT_ROOT / "pyproject.toml"


def read_runtime_requirements() -> list[str]:
    """Read the simple PEP 508 dependency list without third-party parsers."""
    content = PYPROJECT_PATH.read_text(encoding="utf-8")
    match = re.search(
        r"(?ms)^dependencies\s*=\s*(\[.*?^\])",
        content,
    )
    if not match:
        raise RuntimeError("Could not find [project].dependencies in pyproject.toml")

    requirements = ast.literal_eval(match.group(1))
    if not isinstance(requirements, list) or not all(isinstance(item, str) for item in requirements):
        raise RuntimeError("Invalid dependencies list in pyproject.toml")
    return requirements


def distribution_name(requirement: str) -> str:
    """Extract the distribution name from the requirement used by this project."""
    match = re.match(r"[A-Za-z0-9][A-Za-z0-9._-]*", requirement)
    if not match:
        raise ValueError(f"Unsupported dependency format: {requirement}")
    return match.group(0)


def main() -> None:
    missing: list[str] = []
    for requirement in read_runtime_requirements():
        name = distribution_name(requirement)
        try:
            importlib.metadata.version(name)
        except importlib.metadata.PackageNotFoundError:
            missing.append(requirement)

    if not missing:
        print("All Python dependencies are already installed.")
        return

    print("Installing missing Python dependencies:")
    for requirement in missing:
        print(f"  - {requirement}")

    subprocess.run(
        [sys.executable, "-m", "pip", "install", *missing],
        cwd=PROJECT_ROOT,
        check=True,
    )


if __name__ == "__main__":
    main()
