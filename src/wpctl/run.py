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
    elif args.subcommand == "get":
        _run_post_get(args)
    elif args.subcommand == "show":
        _run_post_show(args)
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
            content_format=args.content_format,
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
            content_format=args.content_format,
        )
    except (FileReadError, WordPressAPIError) as e:
        logger.error(str(e))
        sys.exit(1)


def _run_post_get(args: argparse.Namespace) -> None:
    """記事一覧を取得して表示する。

    Args:
        args: argparseで解析された引数
    """
    from wpctl.commands.get import run as get_run
    try:
        posts, total = get_run(
            search=args.search,
            status=args.status,
            per_page=args.per_page,
            page=args.page,
        )
        _print_posts_table(posts, total, page=args.page, per_page=args.per_page)
    except WordPressAPIError as e:
        logger.error(str(e))
        sys.exit(1)


def _run_post_show(args: argparse.Namespace) -> None:
    """記事の詳細を取得して表示する。

    Args:
        args: argparseで解析された引数
    """
    from wpctl.commands.show import run as show_run
    try:
        post = show_run(post_id=args.post_id)
        _print_post_detail(post, fmt=args.format)
    except WordPressAPIError as e:
        logger.error(str(e))
        sys.exit(1)


def _print_posts_table(posts: list[dict], total: int, page: int, per_page: int) -> None:
    if not posts:
        print("記事が見つかりませんでした。")
        return

    rows = []
    for p in posts:
        rows.append({
            "id": str(p.get("id", "")),
            "status": p.get("status", ""),
            "date": (p.get("date", "") or "")[:10],
            "title": p.get("title", {}).get("rendered", ""),
        })

    w_id = max(len("ID"), max(len(r["id"]) for r in rows))
    w_status = max(len("STATUS"), max(len(r["status"]) for r in rows))
    w_date = max(len("DATE"), max(len(r["date"]) for r in rows))

    header = f"{'ID'.ljust(w_id)}  {'STATUS'.ljust(w_status)}  {'DATE'.ljust(w_date)}  TITLE"
    sep = "-" * len(header)
    print(header)
    print(sep)
    for r in rows:
        print(f"{r['id'].ljust(w_id)}  {r['status'].ljust(w_status)}  {r['date'].ljust(w_date)}  {r['title']}")

    offset = (page - 1) * per_page
    shown_from = offset + 1
    shown_to = offset + len(posts)
    print(f"\n{shown_from}〜{shown_to}件 / 全{total}件")


def _print_post_detail(post: dict, fmt: str = "text") -> None:
    title = post.get("title", {}).get("rendered", "")
    excerpt_html = post.get("excerpt", {}).get("rendered", "")
    content_html = post.get("content", {}).get("rendered", "")

    print(f"ID      : {post.get('id', '')}")
    print(f"タイトル: {title}")
    print(f"状態    : {post.get('status', '')}")
    print(f"日時    : {post.get('date', '')}")
    print(f"リンク  : {post.get('link', '')}")

    if excerpt_html:
        from markdownify import markdownify
        print(f"抜粋    : {markdownify(excerpt_html).strip()}")

    print()
    print("─" * 60)

    if fmt == "md":
        from markdownify import markdownify
        print(markdownify(content_html).strip())
    else:
        print(content_html.strip())
