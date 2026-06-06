import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))


from utils.custom_logger import get_logger

logger = get_logger(__name__)


def example():
    logger.info("Application started")
    print("Hello, World!")


example()
