import argparse
from unittest.mock import MagicMock, patch

import pytest

from wpctl.main import _build_parser
from wpctl.run import run


class TestBuildParser:
    """_build_parser のテスト。引数パースの動作を確認する。"""

    def setup_method(self):
        self.parser = _build_parser()

    def test_post_create_required_args(self):
        """post create に必須引数を渡した場合に正しくパースされること。"""
        args = self.parser.parse_args(["post", "create", "article.md"])
        assert args.command == "post"
        assert args.subcommand == "create"
        assert args.file_path == "article.md"
        assert args.title is None

    def test_post_create_with_title_long(self):
        """post create に --title を渡した場合にタイトルが設定されること。"""
        args = self.parser.parse_args(
            ["post", "create", "--title", "My Article", "article.md"]
        )
        assert args.title == "My Article"

    def test_post_create_with_title_short(self):
        """post create に -t を渡した場合にタイトルが設定されること。"""
        args = self.parser.parse_args(
            ["post", "create", "-t", "Short Title", "article.md"]
        )
        assert args.title == "Short Title"

    def test_post_create_missing_file_path(self):
        """post create に FilePath がない場合は SystemExit が発生すること。"""
        with pytest.raises(SystemExit):
            self.parser.parse_args(["post", "create"])

    def test_post_update_required_args(self):
        """post update に必須引数を渡した場合に正しくパースされること。"""
        args = self.parser.parse_args(
            ["post", "update", "--id", "42", "article.md"]
        )
        assert args.command == "post"
        assert args.subcommand == "update"
        assert args.post_id == 42
        assert args.file_path == "article.md"
        assert args.title is None

    def test_post_update_with_title(self):
        """post update に --title を渡した場合にタイトルが設定されること。"""
        args = self.parser.parse_args(
            ["post", "update", "--id", "1", "--title", "Updated", "article.md"]
        )
        assert args.title == "Updated"

    def test_post_update_missing_id(self):
        """post update に --id がない場合は SystemExit が発生すること。"""
        with pytest.raises(SystemExit):
            self.parser.parse_args(["post", "update", "article.md"])

    def test_post_update_missing_file_path(self):
        """post update に FilePath がない場合は SystemExit が発生すること。"""
        with pytest.raises(SystemExit):
            self.parser.parse_args(["post", "update", "--id", "1"])

    def test_post_update_id_is_int(self):
        """post update の --id は整数として解析されること。"""
        args = self.parser.parse_args(
            ["post", "update", "--id", "99", "article.md"]
        )
        assert isinstance(args.post_id, int)

    def test_no_command_returns_none(self):
        """コマンドなしの場合は command が None になること。"""
        args = self.parser.parse_args([])
        assert args.command is None


class TestRun:
    """run() のルーティング動作を確認する。"""

    def _make_args(self, command, subcommand, **kwargs):
        args = argparse.Namespace(command=command, subcommand=subcommand, **kwargs)
        return args

    @patch("wpctl.run._run_post_create")
    def test_run_post_create_dispatches(self, mock_create):
        """run() が post create を正しくルーティングすること。"""
        args = self._make_args(
            "post", "create", file_path="article.md", title="タイトル未設定"
        )
        run(args)
        mock_create.assert_called_once_with(args)

    @patch("wpctl.run._run_post_update")
    def test_run_post_update_dispatches(self, mock_update):
        """run() が post update を正しくルーティングすること。"""
        args = self._make_args(
            "post", "update", file_path="article.md", post_id=1, title="タイトル未設定"
        )
        run(args)
        mock_update.assert_called_once_with(args)

    def test_run_unknown_command_raises(self):
        """未知のコマンドを渡した場合に ValueError が発生すること。"""
        args = self._make_args("unknown", None)
        with pytest.raises(ValueError):
            run(args)

    def test_run_unknown_subcommand_raises(self):
        """未知のサブコマンドを渡した場合に ValueError が発生すること。"""
        args = self._make_args("post", "unknown", file_path="article.md")
        with pytest.raises(ValueError):
            run(args)


class TestMain:
    """main() のエンドツーエンド動作を確認する。"""

    @patch("wpctl.main.run")
    def test_main_calls_run_with_parsed_args(self, mock_run, monkeypatch):
        """環境変数が設定済みの場合、run() が正しく呼ばれること。"""
        monkeypatch.setenv("WP_SITE_URL", "https://example.com")
        monkeypatch.setenv("WP_USER", "user")
        monkeypatch.setenv("WP_APP_PASSWORD", "pass")
        with patch("sys.argv", ["wpctl", "post", "create", "article.md"]):
            from wpctl.main import main
            main()
        mock_run.assert_called_once()
        called_args = mock_run.call_args[0][0]
        assert called_args.command == "post"
        assert called_args.subcommand == "create"
        assert called_args.file_path == "article.md"

    @patch("wpctl.main.run")
    def test_main_no_command_does_not_call_run(self, mock_run):
        """コマンドなしの場合は run() が呼ばれないこと。"""
        with patch("sys.argv", ["wpctl"]):
            from wpctl.main import main
            main()
        mock_run.assert_not_called()


class TestValidateEnv:
    """_validate_env() の環境変数チェックを確認する。"""

    def test_exits_when_both_missing(self, monkeypatch):
        """両方の環境変数が未設定の場合は SystemExit(1) になること。"""
        monkeypatch.delenv("WP_SITE_URL", raising=False)
        monkeypatch.delenv("WP_USER", raising=False)
        monkeypatch.delenv("WP_APP_PASSWORD", raising=False)
        from wpctl.main import _validate_env
        with pytest.raises(SystemExit) as exc_info:
            _validate_env()
        assert exc_info.value.code == 1

    def test_exits_when_one_missing(self, monkeypatch):
        """片方の環境変数が未設定の場合も SystemExit(1) になること。"""
        monkeypatch.setenv("WP_SITE_URL", "https://example.com")
        monkeypatch.setenv("WP_USER", "user")
        monkeypatch.delenv("WP_APP_PASSWORD", raising=False)
        from wpctl.main import _validate_env
        with pytest.raises(SystemExit) as exc_info:
            _validate_env()
        assert exc_info.value.code == 1

    def test_passes_when_all_set(self, monkeypatch):
        """全ての環境変数が設定されている場合は正常終了すること。"""
        monkeypatch.setenv("WP_SITE_URL", "https://example.com")
        monkeypatch.setenv("WP_USER", "user")
        monkeypatch.setenv("WP_APP_PASSWORD", "pass")
        from wpctl.main import _validate_env
        _validate_env()  # 例外が発生しないこと

    def test_error_message_contains_var_name(self, monkeypatch, capsys):
        """エラーメッセージに未設定の変数名が含まれること。"""
        monkeypatch.delenv("WP_SITE_URL", raising=False)
        monkeypatch.delenv("WP_USER", raising=False)
        monkeypatch.delenv("WP_APP_PASSWORD", raising=False)
        from wpctl.main import _validate_env
        with pytest.raises(SystemExit):
            _validate_env()
        captured = capsys.readouterr()
        assert "WP_SITE_URL" in captured.err
        assert "WP_USER" in captured.err
        assert "WP_APP_PASSWORD" in captured.err
