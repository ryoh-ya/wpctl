from wpctl.api.api_wordpress import ApiWordpress
from wpctl.libs.file_reader import read_file
from wpctl.utils.custom_logger import get_logger

logger = get_logger(__name__)


def run(file_path: str, post_id: int, title: str) -> dict:
    """記事を更新する。

    Args:
        file_path: 投稿するファイルのパス（.txt / .html / .md）
        post_id: 更新する記事のID
        title: 記事のタイトル

    Returns:
        WordPress API のレスポンスデータ
    """
    content = read_file(file_path)
    api = ApiWordpress()
    result = api.update_post(post_id=post_id, title=title, content=content)
    logger.info(
        f"記事を更新しました: id={result.get('id')}, link={result.get('link')}"
    )
    return result
