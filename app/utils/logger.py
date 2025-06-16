import logging

logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    level=logging.INFO  # or DEBUG for verbose logging
)

logger = logging.getLogger("binge-pal")
