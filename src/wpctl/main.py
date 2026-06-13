import argparse
import os
import sys

from wpctl.run import run
from wpctl.utils.custom_logger import get_logger

logger = get_logger(__name__)

_REQUIRED_ENV_VARS = ["WP_SITE_URL", "WP_USER", "WP_APP_PASSWORD"]


def _validate_env() -> None:
    """必須環境変数が設定されているか検証する。

    Raises:
        SystemExit: 未設定の環境変数が存在する場合
    """
    missing = [var for var in _REQUIRED_ENV_VARS if not os.environ.get(var)]
    if missing:
        for var in missing:
            print(f"Error: 環境変数 {var} が設定されていません。", file=sys.stderr)
        sys.exit(1)


def _build_parser() -> argparse.ArgumentParser:
    """CLIパーサーを構築する。

    Returns:
        ArgumentParser: 構築済みのパーサー
    """
    parser = argparse.ArgumentParser(
        prog="wpctl",
        description="WordPress APIを活用して記事を投稿・管理するCLIツール",
    )
    subparsers = parser.add_subparsers(dest="command")

    post_parser = subparsers.add_parser("post", help="記事を管理する")
    post_subparsers = post_parser.add_subparsers(dest="subcommand")

    create_parser = post_subparsers.add_parser("create", help="記事を投稿する")
    create_parser.add_argument(
        "file_path", metavar="FilePath", nargs="?", default=None,
        help="投稿するファイルのパス（--content と排他）",
    )
    create_parser.add_argument(
        "--content", "-c",
        default=None,
        help="投稿するHTML文字列（FilePath と排他）",
    )
    create_parser.add_argument(
        "--title", "-t",
        default=None,
        help="タイトル（省略時: Markdownの第一見出し / デフォルト: タイトル未設定）",
    )
    create_parser.add_argument(
        "--status", "-s",
        choices=["draft", "publish"],
        default="draft",
        help="記事のステータス（デフォルト: draft）",
    )
    create_parser.add_argument(
        "--excerpt", "-e",
        default=None,
        help="記事の抜粋",
    )
    create_parser.add_argument(
        "--categories",
        default=None,
        help="カテゴリーIDまたは名前（カンマ区切り、例: 1,2,3）",
    )
    create_parser.add_argument(
        "--tags",
        default=None,
        help="タグIDまたは名前（カンマ区切り、例: tech,python）",
    )

    update_parser = post_subparsers.add_parser("update", help="記事を更新する")
    update_parser.add_argument(
        "file_path", metavar="FilePath", nargs="?", default=None,
        help="投稿するファイルのパス（--content と排他）",
    )
    update_parser.add_argument(
        "--content", "-c",
        default=None,
        help="投稿するHTML文字列（FilePath と排他）",
    )
    update_parser.add_argument(
        "--id", dest="post_id", type=int, required=True, help="更新する記事のID"
    )
    update_parser.add_argument(
        "--title", "-t",
        default=None,
        help="タイトル（省略時: Markdownの第一見出し / デフォルト: タイトル未設定）",
    )
    update_parser.add_argument(
        "--status", "-s",
        choices=["draft", "publish"],
        default=None,
        help="記事のステータス（省略時: 現在のステータスを維持）",
    )
    update_parser.add_argument(
        "--excerpt", "-e",
        default=None,
        help="記事の抜粋",
    )
    update_parser.add_argument(
        "--categories",
        default=None,
        help="カテゴリーIDまたは名前（カンマ区切り、例: 1,2,3）",
    )
    update_parser.add_argument(
        "--tags",
        default=None,
        help="タグIDまたは名前（カンマ区切り、例: tech,python）",
    )

    return parser


def main():
    """エントリーポイント。CLI引数を解析してrunに渡す。"""
    parser = _build_parser()
    args = parser.parse_args()

    if args.command is None:
        parser.print_help()
        return

    _validate_env()
    logger.info(f"wpctl {args.command} {args.subcommand}")
    run(args)


if __name__ == "__main__":
    main()
