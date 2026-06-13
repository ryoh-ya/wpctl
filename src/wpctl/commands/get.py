from wpctl.api.api_wordpress import ApiWordpress
from wpctl.utils.custom_logger import get_logger

logger = get_logger(__name__)


def run(
    search: str | None = None,
    status: str = "any",
    per_page: int = 10,
    page: int = 1,
) -> tuple[list[dict], int]:
    """記事一覧を取得する。

    Args:
        search: 検索キーワード
        status: ステータスフィルター（'publish' / 'draft' / 'any'）
        per_page: 1ページあたりの件数
        page: ページ番号

    Returns:
        (記事リスト, 総件数) のタプル
    """
    api = ApiWordpress()
    posts, total = api.get_posts(search=search, status=status, per_page=per_page, page=page)
    logger.info(f"記事一覧を取得しました: {len(posts)}件 / 全{total}件")
    return posts, total
