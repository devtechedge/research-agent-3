from pathlib import Path

from .orchestrator import run_daily_pipeline


def main() -> None:
    run_daily_pipeline(Path("outputs"))


if __name__ == "__main__":
    main()
