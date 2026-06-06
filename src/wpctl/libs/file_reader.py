from pathlib import Path

from wpctl.libs.md_to_html import convert
from wpctl.utils.custom_logger import get_logger

logger = get_logger(__name__)

SUPPORTED_EXTENSIONS = {".txt", ".html", ".md"}


class FileReadError(Exception):
    """ファイル読み込みエラー。"""


def read_file(file_path: str) -> str:
    """ファイルを読み込んで文字列として返す。

    Markdownファイルはサニタイズ済みHTMLに変換して返す。
    .txt / .html はそのまま返す。

    Args:
        file_path: 読み込むファイルのパス

    Returns:
        ファイルの内容（Markdownの場合はHTML変換済み）

    Raises:
        FileReadError: ファイルが存在しない、または未対応の拡張子の場合
    """
    path = Path(file_path)

    if not path.exists():
        raise FileReadError(f"ファイルが見つかりません: {file_path}")

    ext = path.suffix.lower()
    if ext not in SUPPORTED_EXTENSIONS:
        supported = ", ".join(sorted(SUPPORTED_EXTENSIONS))
        raise FileReadError(
            f"未対応のファイル形式です: {ext}（対応形式: {supported}）"
        )

    text = path.read_text(encoding="utf-8")
    logger.info(f"ファイルを読み込みました: {file_path}")

    if ext == ".md":
        return convert(text)

    return text
