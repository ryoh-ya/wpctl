import markdown
import nh3

_ALLOWED_TAGS = {
    "p", "br", "strong", "b", "em", "i", "u", "s",
    "h1", "h2", "h3", "h4", "h5", "h6",
    "ul", "ol", "li", "dl", "dt", "dd",
    "blockquote", "pre", "code",
    "table", "thead", "tbody", "tr", "th", "td",
    "a", "img", "hr",
}

_ALLOWED_ATTRIBUTES: dict[str, set[str]] = {
    "a": {"href", "title", "target"},
    "img": {"src", "alt", "width", "height"},
    "td": {"colspan", "rowspan"},
    "th": {"colspan", "rowspan"},
    "code": {"class"},
    "pre": {"class"},
}


def convert(text: str) -> str:
    """MarkdownをサニタイズされたHTMLに変換する。

    script タグ・イベント属性・外部JavaScript埋め込みを除去する。

    Args:
        text: Markdown形式のテキスト

    Returns:
        サニタイズ済みのHTML文字列
    """
    html = markdown.markdown(text, extensions=["tables", "fenced_code"])
    return nh3.clean(html, tags=_ALLOWED_TAGS, attributes=_ALLOWED_ATTRIBUTES)
