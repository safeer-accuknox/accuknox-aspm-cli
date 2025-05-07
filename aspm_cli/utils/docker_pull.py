import subprocess
import logging
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
debug_mode = os.getenv('DEBUG', 'FALSE').upper() == 'TRUE'
if debug_mode:
    logging.getLogger().setLevel(logging.DEBUG)

def docker_pull(image: str):
    """Pull a Docker image using subprocess."""
    logger.debug(f"Pulling Docker image: {image}")
    result = subprocess.run(["docker", "pull", image], capture_output=True, text=True)

    if result.returncode != 0:
        logger.error(f"Failed to pull image {image}")
        logger.error(result.stderr)
        raise RuntimeError(f"Failed to pull image: {image}")
    else:
        logger.debug(result.stdout)
        logger.debug(f"Successfully pulled image: {image}")