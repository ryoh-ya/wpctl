from wpctl.utils.custom_logger import get_logger

logger = get_logger(__name__)


def main():
    logger.info("Application started")
    print("Hello, World!")


if __name__ == "__main__":
    main()
