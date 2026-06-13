from wpctl.api.api_wordpress import ApiWordpress
from wpctl.libs.file_reader import (
    DEFAULT_TITLE,
    convert_markdown_string,
    extract_title_from_markdown,
    read_file,
    resolve_title,
)
from wpctl.utils.custom_logger import get_logger

logger = get_logger(__name__)


def run(
    file_path: str | None = None,
    content: str | None = None,
    title: str | None = None,
    status: str = "draft",
    excerpt: str | None = None,
    categories: list[str] | None = None,
    tags: list[str] | None = None,
    content_format: str = "html",
) -> dict:
    """記事を投稿する。

    Args:
        file_path: 投稿するファイルのパス（.txt / .html / .md）。content と排他。
        content: 投稿するコンテンツ文字列。file_path と排他。
        title: 記事のタイトル（None の場合はファイルまたはコンテンツから自動解決）
        status: 記事のステータス（'draft' または 'publish'）
        excerpt: 記事の抜粋
        categories: カテゴリー名またはIDのリスト
        tags: タグ名またはIDのリスト
        content_format: content の形式（'html' または 'md'）。file_path 指定時は無視。

    Returns:
        WordPress API のレスポンスデータ
    """
    api = ApiWordpress()

    if file_path is not None:
        resolved_title = resolve_title(file_path, title)
        html_content = read_file(file_path, strip_h1=(title is None))
    elif content_format == "md":
        raw = content or ""
        if title is None:
            resolved_title = extract_title_from_markdown(raw) or DEFAULT_TITLE
            html_content = convert_markdown_string(raw, strip_h1=True)
        else:
            resolved_title = title
            html_content = convert_markdown_string(raw)
    else:
        resolved_title = title or DEFAULT_TITLE
        html_content = content or ""

    resolved_cats = api.resolve_category_ids(categories) if categories else None
    resolved_tags = api.resolve_tag_ids(tags) if tags else None

    result = api.create_post(
        title=resolved_title,
        content=html_content,
        status=status,
        excerpt=excerpt,
        categories=resolved_cats,
        tags=resolved_tags,
    )
    logger.info(f"記事を投稿しました: id={result.get('id')}, link={result.get('link')}, status={status}")
    return result
