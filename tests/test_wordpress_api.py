from unittest.mock import MagicMock, patch

import pytest
import requests

from wpctl.api.api_wordpress import ApiWordpress, WordPressAPIError


@pytest.fixture(autouse=True)
def set_env(monkeypatch):
    """全テストに WordPress 環境変数を設定する。"""
    monkeypatch.setenv("WP_SITE_URL", "https://example.com")
    monkeypatch.setenv("WP_USER", "user")
    monkeypatch.setenv("WP_APP_PASSWORD", "pass")


def _mock_response(status_code: int, json_data: dict) -> MagicMock:
    mock = MagicMock()
    mock.status_code = status_code
    mock.json.return_value = json_data
    if status_code >= 400:
        mock.raise_for_status.side_effect = requests.exceptions.HTTPError(
            response=mock
        )
    else:
        mock.raise_for_status.return_value = None
    return mock


class TestApiWordpressInit:
    """ApiWordpress の初期化テスト。"""

    def test_init_reads_env_vars(self):
        """インスタンス化時に環境変数を読み込むこと。"""
        api = ApiWordpress()
        assert api._site_url == "https://example.com"
        assert api._auth == ("user", "pass")

    def test_trailing_slash_stripped(self, monkeypatch):
        """WP_SITE_URL の末尾スラッシュが除去されること。"""
        monkeypatch.setenv("WP_SITE_URL", "https://example.com/")
        api = ApiWordpress()
        assert api._site_url == "https://example.com"


class TestCreatePost:
    """ApiWordpress.create_post() のテスト。"""

    @patch("wpctl.api.api_wordpress.requests.post")
    def test_create_post_success(self, mock_post):
        """正常に記事を投稿できること。"""
        mock_post.return_value = _mock_response(
            201, {"id": 1, "link": "https://example.com/?p=1"}
        )
        api = ApiWordpress()
        result = api.create_post(title="タイトル", content="<p>本文</p>")
        assert result["id"] == 1
        mock_post.assert_called_once()

    @patch("wpctl.api.api_wordpress.requests.post")
    def test_create_post_calls_correct_url(self, mock_post):
        """正しいエンドポイントを呼び出すこと。"""
        mock_post.return_value = _mock_response(201, {"id": 1, "link": ""})
        api = ApiWordpress()
        api.create_post(title="タイトル", content="<p>本文</p>")
        called_url = mock_post.call_args[0][0]
        assert called_url == "https://example.com/wp-json/wp/v2/posts"

    @patch("wpctl.api.api_wordpress.requests.post")
    def test_create_post_default_status_publish(self, mock_post):
        """デフォルトのステータスが publish であること。"""
        mock_post.return_value = _mock_response(201, {"id": 1, "link": ""})
        api = ApiWordpress()
        api.create_post(title="タイトル", content="<p>本文</p>")
        payload = mock_post.call_args[1]["json"]
        assert payload["status"] == "publish"

    @patch("wpctl.api.api_wordpress.requests.post")
    def test_create_post_http_error_raises(self, mock_post):
        """HTTP エラー時に WordPressAPIError が発生すること。"""
        mock_post.return_value = _mock_response(401, {})
        api = ApiWordpress()
        with pytest.raises(WordPressAPIError, match="記事の投稿に失敗"):
            api.create_post(title="タイトル", content="<p>本文</p>")


class TestUpdatePost:
    """ApiWordpress.update_post() のテスト。"""

    @patch("wpctl.api.api_wordpress.requests.post")
    def test_update_post_success(self, mock_post):
        """正常に記事を更新できること。"""
        mock_post.return_value = _mock_response(
            200, {"id": 42, "link": "https://example.com/?p=42"}
        )
        api = ApiWordpress()
        result = api.update_post(post_id=42, title="新タイトル", content="<p>新本文</p>")
        assert result["id"] == 42
        mock_post.assert_called_once()

    @patch("wpctl.api.api_wordpress.requests.post")
    def test_update_post_calls_correct_url(self, mock_post):
        """記事IDを含む正しいエンドポイントを呼び出すこと。"""
        mock_post.return_value = _mock_response(200, {"id": 42, "link": ""})
        api = ApiWordpress()
        api.update_post(post_id=42, title="タイトル", content="<p>本文</p>")
        called_url = mock_post.call_args[0][0]
        assert called_url == "https://example.com/wp-json/wp/v2/posts/42"

    @patch("wpctl.api.api_wordpress.requests.post")
    def test_update_post_not_found_raises(self, mock_post):
        """404 エラー時に WordPressAPIError が発生すること。"""
        mock_post.return_value = _mock_response(404, {})
        api = ApiWordpress()
        with pytest.raises(WordPressAPIError, match="記事の更新に失敗"):
            api.update_post(post_id=99, title="タイトル", content="<p>本文</p>")

    @patch("wpctl.api.api_wordpress.requests.post")
    def test_update_post_payload(self, mock_post):
        """title と content が正しく送信されること。"""
        mock_post.return_value = _mock_response(200, {"id": 1, "link": ""})
        api = ApiWordpress()
        api.update_post(post_id=1, title="新タイトル", content="<p>新本文</p>")
        payload = mock_post.call_args[1]["json"]
        assert payload["title"] == "新タイトル"
        assert payload["content"] == "<p>新本文</p>"
