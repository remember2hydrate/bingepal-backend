import logging
from logging.handlers import RotatingFileHandler
from collections import deque

# Create buffer for recent logs
log_buffer = deque(maxlen=100)

class InMemoryHandler(logging.Handler):
    def emit(self, record):
        log_entry = self.format(record)
        log_buffer.append(log_entry)

# Logger config
logger = logging.getLogger("bingepal")
logger.setLevel(logging.INFO)

formatter = logging.Formatter(
    "%(asctime)s - %(levelname)s - %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
)

# Console handler
console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)

# In-memory handler
memory_handler = InMemoryHandler()
memory_handler.setFormatter(formatter)

# Avoid duplicate handlers
if not logger.hasHandlers():
    logger.addHandler(console_handler)
    logger.addHandler(memory_handler)

# Expose the log buffer
def get_recent_logs():
    return list(log_buffer)