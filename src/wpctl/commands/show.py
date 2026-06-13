from wpctl.api.api_wordpress import ApiWordpress
from wpctl.utils.custom_logger import get_logger

logger = get_logger(__name__)


def run(post_id: int) -> dict:
    """記事の詳細を取得する。

    Args:
        post_id: 取得する記事のID

    Returns:
        WordPress API のレスポンスデータ
    """
    api = ApiWordpress()
    result = api.get_post(post_id=post_id)
    title = result.get("title", {}).get("rendered", "")
    logger.info(f"記事を取得しました: id={post_id}, title={title}")
    return result
