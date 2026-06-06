import pytest
from wpctl.utils.custom_logger import get_logger

from wpctl.main import main


def test_main(capsys):
    """mainが正しく実行されることを確認"""
    main()
    captured = capsys.readouterr()
    assert "Hello, World!" in captured.out


def test_main_no_exception():
    """mainが例外を発生させないことを確認"""
    try:
        main()
    except Exception as e:
        pytest.fail(f"main() raised an exception: {e}")


def test_logger_initialization():
    """ロガーが正しく初期化されることを確認"""
    logger = get_logger()
    logger.info("This is a test log message.")
    assert logger is not None
    assert logger.name == "wpctl.main"
