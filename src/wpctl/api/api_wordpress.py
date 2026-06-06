import os

import requests

from wpctl.utils.custom_logger import get_logger

logger = get_logger(__name__)


class WordPressAPIError(Exception):
    """WordPress API 呼び出しエラー。"""


class ApiWordpress:
    """WordPress REST API クライアント。

    Notes:
        WordPress REST API のエンドポイントは通常 /wp-json/wp/v2/
    """

    def __init__(self) -> None:
        self._site_url = os.environ["WP_SITE_URL"].rstrip("/")
        self._auth = (os.environ["WP_USER"], os.environ["WP_APP_PASSWORD"])

    def get_me(self) -> dict:
        """認証情報の疎通確認。

        Returns:
            認証ユーザーの情報

        Raises:
            WordPressAPIError: API呼び出しに失敗した場合
        """
        url = f"{self._site_url}/wp-json/wp/v2/users/me"
        try:
            response = requests.get(url, auth=self._auth)
            response.raise_for_status()
        except requests.exceptions.HTTPError as e:
            logger.error(f"認証に失敗しました: {e}")
            raise WordPressAPIError(f"認証に失敗しました: {e}") from e
        logger.info(
            f"Authentication successful for user: {response.json().get('name')}"
        )
        return response.json()

    def create_post(
        self,
        title: str,
        content: str,
        status: str = "publish",
    ) -> dict:
        """新しい記事を投稿する。

        Args:
            title: 記事のタイトル
            content: 記事の内容（HTML）
            status: 記事のステータス（'publish' または 'draft'）

        Returns:
            作成された記事の情報

        Raises:
            WordPressAPIError: API呼び出しに失敗した場合
        """
        url = f"{self._site_url}/wp-json/wp/v2/posts"
        payload = {"title": title, "content": content, "status": status}
        try:
            response = requests.post(url, json=payload, auth=self._auth)
            response.raise_for_status()
        except requests.exceptions.HTTPError as e:
            logger.error(f"記事の投稿に失敗しました: {e}")
            raise WordPressAPIError(f"記事の投稿に失敗しました: {e}") from e
        logger.info(f"Post created successfully: {response.json().get('link')}")
        return response.json()

    def update_post(
        self,
        post_id: int,
        title: str,
        content: str,
    ) -> dict:
        """既存の記事を更新する。

        Args:
            post_id: 更新する記事のID
            title: 更新後のタイトル
            content: 更新後の内容（HTML）

        Returns:
            更新された記事の情報

        Raises:
            WordPressAPIError: API呼び出しに失敗した場合
        """
        url = f"{self._site_url}/wp-json/wp/v2/posts/{post_id}"
        payload = {"title": title, "content": content}
        try:
            response = requests.post(url, json=payload, auth=self._auth)
            response.raise_for_status()
        except requests.exceptions.HTTPError as e:
            logger.error(f"記事の更新に失敗しました: id={post_id}, {e}")
            raise WordPressAPIError(f"記事の更新に失敗しました: {e}") from e
        logger.info(f"Post updated successfully: {response.json().get('link')}")
        return response.json()
