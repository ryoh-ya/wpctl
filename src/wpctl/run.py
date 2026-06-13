import argparse
import sys

from wpctl.api.api_wordpress import WordPressAPIError
from wpctl.libs.file_reader import FileReadError
from wpctl.utils.custom_logger import get_logger

logger = get_logger(__name__)


def run(args: argparse.Namespace) -> None:
    """ツールのロジック開始点。コマンドに応じた処理を呼び出す。

    Args:
        args: argparseで解析された引数
    """
    if args.command == "post":
        _run_post(args)
    else:
        raise ValueError(f"Unknown command: {args.command}")


def _run_post(args: argparse.Namespace) -> None:
    """post コマンドのサブコマンドを振り分ける。

    Args:
        args: argparseで解析された引数
    """
    if args.subcommand == "create":
        _run_post_create(args)
    elif args.subcommand == "update":
        _run_post_update(args)
    else:
        raise ValueError(f"Unknown subcommand: {args.subcommand}")


def _parse_csv(value: str | None) -> list[str] | None:
    if value is None:
        return None
    return [v.strip() for v in value.split(",") if v.strip()]


def _validate_content_source(args: argparse.Namespace) -> None:
    if args.file_path is None and args.content is None:
        logger.error("FilePath または --content のいずれかを指定してください。")
        sys.exit(1)
    if args.file_path is not None and args.content is not None:
        logger.error("FilePath と --content は同時に指定できません。")
        sys.exit(1)


def _run_post_create(args: argparse.Namespace) -> None:
    """記事を投稿する。

    Args:
        args: argparseで解析された引数
    """
    _validate_content_source(args)
    from wpctl.commands.create import run as create_run
    try:
        create_run(
            file_path=args.file_path,
            content=args.content,
            title=args.title,
            status=args.status,
            excerpt=args.excerpt,
            categories=_parse_csv(args.categories),
            tags=_parse_csv(args.tags),
        )
    except (FileReadError, WordPressAPIError) as e:
        logger.error(str(e))
        sys.exit(1)


def _run_post_update(args: argparse.Namespace) -> None:
    """記事を更新する。

    Args:
        args: argparseで解析された引数
    """
    _validate_content_source(args)
    from wpctl.commands.update import run as update_run
    try:
        update_run(
            file_path=args.file_path,
            content=args.content,
            post_id=args.post_id,
            title=args.title,
            status=args.status,
            excerpt=args.excerpt,
            categories=_parse_csv(args.categories),
            tags=_parse_csv(args.tags),
        )
    except (FileReadError, WordPressAPIError) as e:
        logger.error(str(e))
        sys.exit(1)
