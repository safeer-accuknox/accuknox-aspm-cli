import logging
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
debug_mode = os.getenv('DEBUG', 'FALSE').upper() == 'TRUE'
if debug_mode:
    logging.getLogger().setLevel(logging.DEBUG)

def handle_failure(exit_code, soft_fail):
    """Handle pipeline success or failure based on soft fail flag."""
    if exit_code != 0:
        if soft_fail:
            logger.warning("Vulnerabilities detected, but soft fail is enabled. Continuing...")
        else:
            logger.error("Vulnerabilities detected and soft fail is disabled. Exiting with failure.")
            exit(1)
    else:
        logger.info("Scan completed successfully.")