import argparse

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


def _run_post_create(args: argparse.Namespace) -> None:
    """記事投稿のロジック。

    Args:
        args: argparseで解析された引数
            file_path: 投稿するファイルのパス
            title: 記事のタイトル
    """
    logger.info(f"post create: file={args.file_path}, title={args.title}")
    # TODO: WordPress API 連携


def _run_post_update(args: argparse.Namespace) -> None:
    """記事更新のロジック。

    Args:
        args: argparseで解析された引数
            file_path: 投稿するファイルのパス
            post_id: 更新する記事のID
            title: 記事のタイトル
    """
    logger.info(
        f"post update: id={args.post_id}, file={args.file_path}, title={args.title}"
    )
    # TODO: WordPress API 連携
