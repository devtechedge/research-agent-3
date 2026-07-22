import logging
from pathlib import Path

from .config import settings
from .orchestrator import run_daily_pipeline

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(Path("lyme_agent.log"), encoding="utf-8")
    ]
)

logger = logging.getLogger(__name__)


def main() -> None:
    logger.info("Starting Lyme Research Agent pipeline")
    logger.info(f"Environment: {settings.environment}")
    logger.info(f"Simulation mode: {settings.simulation_mode}")
    try:
        report_path = run_daily_pipeline(Path("outputs"), enable_verification=False)
        logger.info(f"Pipeline completed successfully. Report saved to: {report_path}")
    except Exception as e:
        logger.error(f"Pipeline failed: {e}", exc_info=True)
        raise


if __name__ == "__main__":
    main()
