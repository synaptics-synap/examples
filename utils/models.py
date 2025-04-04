import os
import requests
import logging
from huggingface_hub import hf_hub_download

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def download(repo_id, filename):
    base_dir = "./models"
    local_file = os.path.join(base_dir, repo_id, filename)
    os.makedirs(os.path.dirname(local_file), exist_ok=True)

    if os.path.exists(local_file):
        logger.info(f"File found locally at: {local_file}")
        return local_file

    local_server = os.environ.get("SYNAPTICS_SERVER_IP")

    if local_server:
        url = f"http://{local_server}/downloads/models/{repo_id}/{filename}"
        logger.debug(f"Constructed URL: {url}")

        try:
            r = requests.get(url, timeout=5)
            if r.status_code == 200:
                with open(local_file, "wb") as f:
                    f.write(r.content)
                logger.debug("File downloaded from local server.")
                return local_file
            else:
                logger.debug(
                    f"Local server error (status: {r.status_code}). Falling back to Hugging Face."
                )
        except Exception as e:
            logger.debug(f"Error fetching from local server: {e}")
    else:
        logger.debug("SYNAPTICS_SERVER_IP not set. Skipping local server attempt.")

    logger.info("Attempting to download model from Hugging Face Hub.")
    downloaded_file = hf_hub_download(
        repo_id=repo_id,
        filename=filename,
        local_dir=os.path.join(base_dir, repo_id),
    )
    logger.debug("Download from Hugging Face completed.")
    return downloaded_file
