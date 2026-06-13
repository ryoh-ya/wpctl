import re
from pathlib import Path

from wpctl.libs.md_to_html import convert
from wpctl.utils.custom_logger import get_logger

logger = get_logger(__name__)

SUPPORTED_EXTENSIONS = {".txt", ".html", ".md"}
DEFAULT_TITLE = "タイトル未設定"

_H1_PATTERN = re.compile(r"^#\s+(.+)", re.MULTILINE)


class FileReadError(Exception):
    """ファイル読み込みエラー。"""


def read_file(file_path: str, strip_h1: bool = False) -> str:
    """ファイルを読み込んで文字列として返す。

    Markdownファイルはサニタイズ済みHTMLに変換して返す。
    .txt / .html はそのまま返す。

    Args:
        file_path: 読み込むファイルのパス
        strip_h1: True の場合、Markdownの第一レベル見出しを除去してから変換する

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
        if strip_h1:
            text = _strip_first_h1(text)
        return convert(text)

    return text


def _strip_first_h1(text: str) -> str:
    """Markdownテキストから最初の第一レベル見出し行を除去する。

    Args:
        text: Markdown形式のテキスト

    Returns:
        第一レベル見出しを除去したテキスト
    """
    stripped = _H1_PATTERN.sub("", text, count=1)
    return stripped.lstrip("\n")


def convert_markdown_string(text: str, strip_h1: bool = False) -> str:
    """Markdown文字列をHTMLに変換する。

    Args:
        text: Markdown形式のテキスト
        strip_h1: True の場合、第一レベル見出しを除去してから変換する

    Returns:
        HTML文字列
    """
    if strip_h1:
        text = _strip_first_h1(text)
    return convert(text)


def extract_title_from_markdown(text: str) -> str | None:
    """Markdown文字列から第一レベル見出しのテキストを取得する。

    Args:
        text: Markdown形式のテキスト

    Returns:
        見出しのテキスト。見つからない場合は None
    """
    match = _H1_PATTERN.search(text)
    return match.group(1).strip() if match else None


def resolve_title(file_path: str, title: str | None) -> str:
    """タイトルを解決する。

    優先順位:
        1. 引数で指定されたタイトル（-t / --title）
        2. Markdownファイルの第一レベル見出し（# 見出し）
        3. デフォルト値「タイトル未設定」

    Args:
        file_path: 対象ファイルのパス
        title: CLI引数で指定されたタイトル（未指定の場合は None）

    Returns:
        解決済みのタイトル文字列
    """
    if title is not None:
        return title

    path = Path(file_path)
    if path.exists() and path.suffix.lower() == ".md":
        text = path.read_text(encoding="utf-8")
        match = _H1_PATTERN.search(text)
        if match:
            return match.group(1).strip()

    return DEFAULT_TITLE
