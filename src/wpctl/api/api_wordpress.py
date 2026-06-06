import os
import requests

from wpctl.utils.custom_logger import get_logger

logger = get_logger()


class ApiWordpress:
    """
    WordPress REST APIを利用して記事の投稿や更新を行うクラス

    Notes:
        - WordPress REST APIのエンドポイントは通常 /wp-json/wp/v2/
    """

    WP_SITE_URL = os.getenv("WP_SITE_URL")
    WP_USER = os.getenv("WP_USER")
    WP_APP_PASSWORD = os.getenv("WP_APP_PASSWORD")

    @classmethod
    def _get_headers(cls) -> dict:
        """
        ヘッダー情報を取得する

        Returns:
            dict: APIリクエスト用のヘッダー情報
        """
        return {
            "Content-Type": "application/json",
        }

    @classmethod
    def get_me(cls):
        """認証情報が正しいか確認するためのテストメソッド"""
        url = f"{cls.WP_SITE_URL}/wp-json/wp/v2/users/me"
        response = requests.get(url, auth=(cls.WP_USER, cls.WP_APP_PASSWORD))
        response.raise_for_status()
        logger.info(
            f"Authentication successful for user: {response.json().get('name')}"
        )
        return response.json()

    @classmethod
    def create_post(
        cls,
        title: str,
        content: str,
        categories: list[int] = None,
        status: str = "draft",
    ) -> dict:
        """新しい記事を作成する

        Args:
            title (str): 記事のタイトル
            content (str): 記事の内容
            categories (list[int], optional): カテゴリーIDのリスト。デフォルトはNone
            status (str, optional): 記事のステータス(例: 'draft', 'publish')
        Returns:
            dict: 作成された記事の情報
        """
        url = f"{cls.WP_SITE_URL}/wp-json/wp/v2/posts"
        payload = {
            "title": title,
            "content": content,
            "status": status,  # 下書き状態で投稿
        }
        if categories:
            payload["categories"] = categories

        response = requests.post(
            url, json=payload, auth=(cls.WP_USER, cls.WP_APP_PASSWORD)
        )
        response.raise_for_status()
        logger.info(f"Post created successfully: {response.json().get('link')}")
        return response.json()

    @classmethod
    def update_post(
        cls,
        post_id: int,
        title: str = None,
        content: str = None,
        categories: list[int] = None,
    ) -> dict:
        """既存の記事を更新する

        Args:
            post_id (int): 更新する記事のID
            title (str, optional): 更新したいタイトル
            content (str, optional): 更新したい内容
            categories (list[int], optional): 更新したいカテゴリーIDのリスト
        """
        url = f"{cls.WP_SITE_URL}/wp-json/wp/v2/posts/{post_id}"
        payload = {}
        if title:
            payload["title"] = title
        if content:
            payload["content"] = content
        if categories is not None:
            payload["categories"] = categories

        response = requests.post(
            url, json=payload, auth=(cls.WP_USER, cls.WP_APP_PASSWORD)
        )
        response.raise_for_status()
        logger.info(f"Post updated successfully: {response.json().get('link')}")
        return response.json()
