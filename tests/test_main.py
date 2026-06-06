from unittest.mock import patch

from wpctl.utils.custom_logger import get_logger

from wpctl.main import main


def test_main_no_args_prints_help(capsys):
    """コマンドなしで main() を呼んでも例外が発生しないこと。"""
    with patch("sys.argv", ["wpctl"]):
        main()
    captured = capsys.readouterr()
    assert "wpctl" in captured.out


def test_main_no_exception():
    """コマンドなしで main() が例外を発生させないこと。"""
    with patch("sys.argv", ["wpctl"]):
        try:
            main()
        except SystemExit:
            pass  # argparse の --help は SystemExit を発生させる場合がある
        except Exception as e:
            raise AssertionError(f"main() raised an unexpected exception: {e}")


def test_logger_initialization():
    """ロガーが正しく初期化されること。"""
    logger = get_logger()
    logger.info("This is a test log message.")
    assert logger is not None
