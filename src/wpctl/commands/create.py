from wpctl.api.api_wordpress import ApiWordpress
from wpctl.libs.file_reader import read_file
from wpctl.utils.custom_logger import get_logger

logger = get_logger(__name__)


def run(file_path: str, title: str) -> dict:
    """記事を投稿する。

    Args:
        file_path: 投稿するファイルのパス（.txt / .html / .md）
        title: 記事のタイトル

    Returns:
        WordPress API のレスポンスデータ
    """
    content = read_file(file_path)
    api = ApiWordpress()
    result = api.create_post(title=title, content=content)
    logger.info(f"記事を投稿しました: id={result.get('id')}, link={result.get('link')}")
    return result
