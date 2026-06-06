from wpctl.api.api_wordpress import ApiWordpress
from wpctl.libs.file_reader import read_file, resolve_title
from wpctl.utils.custom_logger import get_logger

logger = get_logger(__name__)


def run(file_path: str, post_id: int, title: str | None) -> dict:
    """記事を更新する。

    Args:
        file_path: 投稿するファイルのパス（.txt / .html / .md）
        post_id: 更新する記事のID
        title: 記事のタイトル（None の場合はファイルから自動解決）

    Returns:
        WordPress API のレスポンスデータ
    """
    resolved = resolve_title(file_path, title)
    content = read_file(file_path, strip_h1=(title is None))
    api = ApiWordpress()
    result = api.update_post(post_id=post_id, title=resolved, content=content)
    logger.info(
        f"記事を更新しました: id={result.get('id')}, link={result.get('link')}"
    )
    return result
