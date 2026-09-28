"""Install missing dependencies and start the TikTokLive Web UI."""

import runpy
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent


def main() -> None:
    runpy.run_path(
        str(PROJECT_ROOT / "scripts" / "ensure_dependencies.py"),
        run_name="__main__",
    )

    service_path = PROJECT_ROOT / "examples" / "web-ui" / "service.py"
    sys.argv = [str(service_path)]
    runpy.run_path(str(service_path), run_name="__main__")


if __name__ == "__main__":
    main()
