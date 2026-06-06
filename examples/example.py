"""サンプルコード

run:
    set -a; source .env; set +a; python examples/example.py
"""

import sys
import os

sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src"))
)


from wpctl.utils.custom_logger import get_logger

logger = get_logger(__name__)


def example():
    logger.info("Application started")
    print("Hello, World!")


example()
