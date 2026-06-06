import pytest

from wpctl.libs.file_reader import SUPPORTED_EXTENSIONS, FileReadError, read_file
from wpctl.libs.md_to_html import convert


class TestReadFile:
    """read_file() のテスト。"""

    def test_read_txt(self, tmp_path):
        """.txt ファイルをそのまま返すこと。"""
        f = tmp_path / "article.txt"
        f.write_text("Hello, World!", encoding="utf-8")
        assert read_file(str(f)) == "Hello, World!"

    def test_read_html(self, tmp_path):
        """.html ファイルをそのまま返すこと。"""
        f = tmp_path / "article.html"
        f.write_text("<p>Hello</p>", encoding="utf-8")
        assert read_file(str(f)) == "<p>Hello</p>"

    def test_read_md_converts_to_html(self, tmp_path):
        """.md ファイルはHTMLに変換されること。"""
        f = tmp_path / "article.md"
        f.write_text("# Hello\n\nWorld", encoding="utf-8")
        result = read_file(str(f))
        assert "<h1>Hello</h1>" in result
        assert "<p>World</p>" in result

    def test_file_not_found_raises(self):
        """存在しないファイルは FileReadError になること。"""
        with pytest.raises(FileReadError, match="ファイルが見つかりません"):
            read_file("/nonexistent/path/article.md")

    def test_unsupported_extension_raises(self, tmp_path):
        """未対応の拡張子は FileReadError になること。"""
        f = tmp_path / "article.pdf"
        f.write_text("dummy", encoding="utf-8")
        with pytest.raises(FileReadError, match="未対応のファイル形式"):
            read_file(str(f))

    def test_supported_extensions(self):
        """対応拡張子が正しく定義されていること。"""
        assert ".txt" in SUPPORTED_EXTENSIONS
        assert ".html" in SUPPORTED_EXTENSIONS
        assert ".md" in SUPPORTED_EXTENSIONS


class TestConvertMarkdown:
    """md_to_html.convert() のサニタイズ動作を確認する。"""

    def test_basic_conversion(self):
        """基本的なMarkdownがHTMLに変換されること。"""
        result = convert("**bold**")
        assert "<strong>bold</strong>" in result

    def test_script_tag_removed(self):
        """script タグが除去されること。"""
        md = "text\n\n<script>alert('xss')</script>\n\nafter"
        result = convert(md)
        assert "<script>" not in result
        assert "alert" not in result

    def test_event_attribute_removed(self):
        """onerror などのイベント属性が除去されること。"""
        md = '<img src="x" onerror="alert(1)">'
        result = convert(md)
        assert "onerror" not in result

    def test_onclick_removed(self):
        """onclick 属性が除去されること。"""
        md = '<a href="#" onclick="evil()">link</a>'
        result = convert(md)
        assert "onclick" not in result

    def test_href_allowed(self):
        """a タグの href 属性は残ること。"""
        md = "[link](https://example.com)"
        result = convert(md)
        assert 'href="https://example.com"' in result

    def test_img_src_allowed(self):
        """img タグの src / alt 属性は残ること。"""
        md = "![alt text](https://example.com/img.png)"
        result = convert(md)
        assert 'src="https://example.com/img.png"' in result
        assert 'alt="alt text"' in result

    def test_table_converted(self):
        """テーブルが変換されること。"""
        md = "| A | B |\n|---|---|\n| 1 | 2 |"
        result = convert(md)
        assert "<table>" in result
        assert "<td>" in result

    def test_fenced_code_converted(self):
        """コードブロックが変換されること。"""
        md = "```python\nprint('hello')\n```"
        result = convert(md)
        assert "<code" in result
