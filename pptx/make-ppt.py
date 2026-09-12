"""Build the two CDE decks while preserving the original Python entry point."""

from pathlib import Path
import os
import subprocess


def main() -> None:
    directory = Path(__file__).resolve().parent
    node = os.environ.get(
        "RUNTIME_NODE",
        "/Users/jarad/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node",
    )
    environment = os.environ.copy()
    environment.setdefault(
        "RUNTIME_NODE_MODULES",
        "/Users/jarad/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules",
    )
    modules_link = directory / "node_modules"
    if not modules_link.exists():
        modules_link.symlink_to(environment["RUNTIME_NODE_MODULES"])
    subprocess.run([node, str(directory / "build-decks.mjs")], cwd=directory, env=environment, check=True)


if __name__ == "__main__":
    main()
