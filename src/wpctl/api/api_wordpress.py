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

    def _get_or_create_term(self, endpoint: str, name: str) -> int:
        """タームを名前で検索し、存在しない場合は作成してIDを返す。

        Args:
            endpoint: APIエンドポイント名（'tags' または 'categories'）
            name: タームの名前

        Returns:
            タームのID

        Raises:
            WordPressAPIError: API呼び出しに失敗した場合
        """
        url = f"{self._site_url}/wp-json/wp/v2/{endpoint}"
        try:
            resp = requests.get(url, params={"search": name}, auth=self._auth)
            resp.raise_for_status()
            for item in resp.json():
                if item.get("name") == name or item.get("slug") == name.lower().replace(" ", "-"):
                    return item["id"]
            resp = requests.post(url, json={"name": name}, auth=self._auth)
            resp.raise_for_status()
            return resp.json()["id"]
        except requests.exceptions.HTTPError as e:
            raise WordPressAPIError(f"タームの解決に失敗しました: {name}, {e}") from e

    def resolve_category_ids(self, values: list[str]) -> list[int]:
        """カテゴリー名またはIDのリストをIDリストに変換する。

        Args:
            values: カテゴリー名またはIDの文字列リスト

        Returns:
            カテゴリーIDのリスト
        """
        ids = []
        for v in values:
            v = v.strip()
            if not v:
                continue
            ids.append(int(v) if v.isdigit() else self._get_or_create_term("categories", v))
        return ids

    def resolve_tag_ids(self, values: list[str]) -> list[int]:
        """タグ名またはIDのリストをIDリストに変換する。

        Args:
            values: タグ名またはIDの文字列リスト

        Returns:
            タグIDのリスト
        """
        ids = []
        for v in values:
            v = v.strip()
            if not v:
                continue
            ids.append(int(v) if v.isdigit() else self._get_or_create_term("tags", v))
        return ids

    def create_post(
        self,
        title: str,
        content: str,
        status: str = "publish",
        excerpt: str | None = None,
        categories: list[int] | None = None,
        tags: list[int] | None = None,
    ) -> dict:
        """新しい記事を投稿する。

        Args:
            title: 記事のタイトル
            content: 記事の内容（HTML）
            status: 記事のステータス（'publish' または 'draft'）
            excerpt: 記事の抜粋
            categories: カテゴリーIDのリスト
            tags: タグIDのリスト

        Returns:
            作成された記事の情報

        Raises:
            WordPressAPIError: API呼び出しに失敗した場合
        """
        url = f"{self._site_url}/wp-json/wp/v2/posts"
        payload: dict = {"title": title, "content": content, "status": status}
        if excerpt is not None:
            payload["excerpt"] = excerpt
        if categories:
            payload["categories"] = categories
        if tags:
            payload["tags"] = tags
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
        status: str | None = None,
        excerpt: str | None = None,
        categories: list[int] | None = None,
        tags: list[int] | None = None,
    ) -> dict:
        """既存の記事を更新する。

        Args:
            post_id: 更新する記事のID
            title: 更新後のタイトル
            content: 更新後の内容（HTML）
            status: 記事のステータス（None の場合は現在のステータスを維持）
            excerpt: 記事の抜粋
            categories: カテゴリーIDのリスト
            tags: タグIDのリスト

        Returns:
            更新された記事の情報

        Raises:
            WordPressAPIError: API呼び出しに失敗した場合
        """
        url = f"{self._site_url}/wp-json/wp/v2/posts/{post_id}"
        payload: dict = {"title": title, "content": content}
        if status is not None:
            payload["status"] = status
        if excerpt is not None:
            payload["excerpt"] = excerpt
        if categories:
            payload["categories"] = categories
        if tags:
            payload["tags"] = tags
        try:
            response = requests.post(url, json=payload, auth=self._auth)
            response.raise_for_status()
        except requests.exceptions.HTTPError as e:
            logger.error(f"記事の更新に失敗しました: id={post_id}, {e}")
            raise WordPressAPIError(f"記事の更新に失敗しました: {e}") from e
        logger.info(f"Post updated successfully: {response.json().get('link')}")
        return response.json()
