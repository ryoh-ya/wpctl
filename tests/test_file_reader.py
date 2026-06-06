import pytest

from wpctl.libs.file_reader import (
    DEFAULT_TITLE,
    SUPPORTED_EXTENSIONS,
    FileReadError,
    read_file,
    resolve_title,
)
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


class TestResolveTitle:
    """resolve_title() のタイトル解決優先順位を確認する。"""

    def test_explicit_title_wins(self, tmp_path):
        """-t で指定したタイトルが最優先されること。"""
        f = tmp_path / "article.md"
        f.write_text("# ファイルの見出し\n\n本文", encoding="utf-8")
        result = resolve_title(str(f), "引数のタイトル")
        assert result == "引数のタイトル"

    def test_h1_extracted_when_no_title(self, tmp_path):
        """タイトル未指定の場合、# 第一見出しが使われること。"""
        f = tmp_path / "article.md"
        f.write_text("# 記事の見出し\n\n本文", encoding="utf-8")
        result = resolve_title(str(f), None)
        assert result == "記事の見出し"

    def test_second_h1_ignored(self, tmp_path):
        """複数の # 見出しがある場合、最初のものが使われること。"""
        f = tmp_path / "article.md"
        f.write_text("# 第一見出し\n\n## 第二見出し\n\n# 別の第一見出し", encoding="utf-8")
        result = resolve_title(str(f), None)
        assert result == "第一見出し"

    def test_default_when_no_h1_in_md(self, tmp_path):
        """# 見出しがない .md ファイルはデフォルトタイトルになること。"""
        f = tmp_path / "article.md"
        f.write_text("## 第二見出しのみ\n\n本文", encoding="utf-8")
        result = resolve_title(str(f), None)
        assert result == DEFAULT_TITLE

    def test_default_for_txt_file(self, tmp_path):
        """.txt ファイルはデフォルトタイトルになること。"""
        f = tmp_path / "article.txt"
        f.write_text("# これは見出しではない", encoding="utf-8")
        result = resolve_title(str(f), None)
        assert result == DEFAULT_TITLE

    def test_default_for_html_file(self, tmp_path):
        """.html ファイルはデフォルトタイトルになること。"""
        f = tmp_path / "article.html"
        f.write_text("<h1>見出し</h1>", encoding="utf-8")
        result = resolve_title(str(f), None)
        assert result == DEFAULT_TITLE

    def test_h1_stripped(self, tmp_path):
        """# 見出しの前後の空白が除去されること。"""
        f = tmp_path / "article.md"
        f.write_text("#   空白あり見出し   \n\n本文", encoding="utf-8")
        result = resolve_title(str(f), None)
        assert result == "空白あり見出し"

    def test_nonexistent_file_returns_default(self):
        """存在しないファイルはデフォルトタイトルになること。"""
        result = resolve_title("/nonexistent/file.md", None)
        assert result == DEFAULT_TITLE


class TestReadFileStripH1:
    """read_file() の strip_h1 オプションを確認する。"""

    def test_strip_h1_removes_heading_from_content(self, tmp_path):
        """strip_h1=True のとき H1 が本文から除去されること。"""
        f = tmp_path / "article.md"
        f.write_text("# 見出し\n\n本文の段落", encoding="utf-8")
        result = read_file(str(f), strip_h1=True)
        assert "<h1>" not in result
        assert "<p>本文の段落</p>" in result

    def test_strip_h1_false_keeps_heading(self, tmp_path):
        """strip_h1=False（デフォルト）のとき H1 が本文に残ること。"""
        f = tmp_path / "article.md"
        f.write_text("# 見出し\n\n本文の段落", encoding="utf-8")
        result = read_file(str(f), strip_h1=False)
        assert "<h1>見出し</h1>" in result

    def test_strip_h1_no_heading_in_file(self, tmp_path):
        """H1 がないファイルで strip_h1=True でも正常に動作すること。"""
        f = tmp_path / "article.md"
        f.write_text("## 第二見出し\n\n本文", encoding="utf-8")
        result = read_file(str(f), strip_h1=True)
        assert "<h2>" in result
        assert "<p>本文</p>" in result

    def test_strip_h1_only_removes_first(self, tmp_path):
        """strip_h1=True のとき最初の H1 のみ除去されること。"""
        f = tmp_path / "article.md"
        f.write_text("# 第一見出し\n\n本文\n\n# 第二の見出し", encoding="utf-8")
        result = read_file(str(f), strip_h1=True)
        assert "第一見出し" not in result
        assert "<h1>第二の見出し</h1>" in result

    def test_strip_h1_ignored_for_txt(self, tmp_path):
        """strip_h1=True でも .txt ファイルは変更されないこと。"""
        f = tmp_path / "article.txt"
        f.write_text("# これはテキスト", encoding="utf-8")
        result = read_file(str(f), strip_h1=True)
        assert result == "# これはテキスト"
