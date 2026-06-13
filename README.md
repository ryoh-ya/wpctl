# wpctl

* Ver: 1.1.0

WordPress APIを活用して、記事を投稿・管理するCLIツール。

## 概要

MarkDown / テキスト / HTMLファイルを読み込み、WordPress REST APIを通じて記事の投稿・更新を行います。
ファイルパスの代わりに直接コンテンツを渡すことも可能で、Pythonライブラリとしても利用できます。

## 機能

| 機能     | コマンド            | 説明                                       |
| -------- | ------------------- | ------------------------------------------ |
| 記事投稿 | `wpctl post create` | Markdownなどのファイルを記事として投稿する |
| 記事更新 | `wpctl post update` | 既存の記事をファイルの内容で更新する       |

## インストール

```sh
pip install wpctl
```

## 使い方

### 記事を投稿する

```sh
wpctl post create [オプション] [FilePath]
```

| 引数/オプション | フラグ            | 必須 | 説明                                                  |
| --------------- | ----------------- | ---- | ----------------------------------------------------- |
| `FilePath`      |                   |      | 投稿するファイルのパス（`--content` と排他）          |
| `content`       | `--content`, `-c` |      | 投稿するHTML文字列（`FilePath` と排他）               |
| `title`         | `--title`, `-t`   |      | 記事タイトル（デフォルト: Markdownの第一見出し）      |
| `status`        | `--status`, `-s`  |      | ステータス `draft` / `publish`（デフォルト: `draft`） |
| `excerpt`       | `--excerpt`, `-e` |      | 記事の抜粋                                            |
| `categories`    | `--categories`    |      | カテゴリーIDまたは名前（カンマ区切り、例: `1,2,3`）   |
| `tags`          | `--tags`          |      | タグIDまたは名前（カンマ区切り、例: `tech,python`）   |

> `FilePath` と `--content` はどちらか一方を指定してください。

```sh
# ファイルからドラフト投稿（デフォルト）
wpctl post create article.md

# ファイルから公開投稿
wpctl post create --status publish article.md

# HTMLを直接指定してドラフト投稿
wpctl post create --content "<p>本文</p>" --title "記事タイトル"

# カテゴリー・タグ・抜粋を指定して公開
wpctl post create --status publish --categories "1,2" --tags "tech,python" --excerpt "記事の要約" article.md
```

### 記事を更新する

```sh
wpctl post update --id <ID> [オプション] [FilePath]
```

| 引数/オプション | フラグ                | 必須 | 説明                                                           |
| --------------- | --------------------- | ---- | -------------------------------------------------------------- |
| `FilePath`      |                       |      | 投稿するファイルのパス（`--content` と排他）                   |
| `content`       | `--content`, `-c`     |      | 投稿するHTML文字列（`FilePath` と排他）                        |
| `id`            | `--id`                | true | 更新対象の記事ID                                               |
| `title`         | `--title`, `-t`       |      | 記事タイトル（デフォルト: Markdownの第一見出し）               |
| `status`        | `--status`, `-s`      |      | ステータス `draft` / `publish`（省略時: 現在のステータスを維持）|
| `excerpt`       | `--excerpt`, `-e`     |      | 記事の抜粋                                                     |
| `categories`    | `--categories`        |      | カテゴリーIDまたは名前（カンマ区切り、例: `1,2,3`）            |
| `tags`          | `--tags`              |      | タグIDまたは名前（カンマ区切り、例: `tech,python`）            |

```sh
# ファイルで更新
wpctl post update --id 42 article.md

# ステータスをドラフトに変更
wpctl post update --id 42 --status draft article.md

# タグ・カテゴリーを更新
wpctl post update --id 42 --tags "tech,python" --categories "1" article.md
```

## ライブラリとして使う

```python
import os
os.environ["WP_SITE_URL"] = "https://example.com"
os.environ["WP_USER"] = "user"
os.environ["WP_APP_PASSWORD"] = "app-password"

import wpctl

# ファイルからドラフト投稿
result = wpctl.create_post(file_path="article.md")

# HTMLを直接指定して公開投稿
result = wpctl.create_post(
    content="<p>本文</p>",
    title="記事タイトル",
    status="publish",
    excerpt="記事の要約",
    categories=["1", "2"],       # IDまたは名前
    tags=["tech", "python"],     # IDまたは名前
)

# 記事を更新
result = wpctl.update_post(
    file_path="article.md",
    post_id=42,
    status="publish",
)
```

## 環境変数

| 環境変数          | 必須 | 説明                        |
| ----------------- | ---- | --------------------------- |
| `WP_USER`         | true | WordPressのユーザー名       |
| `WP_APP_PASSWORD` | true | WordPressのアプリパスワード |
| `WP_SITE_URL`     | true | WordPressのサイトURL        |

> `.env` ファイルは非対応です。あらかじめシェルの環境変数に設定してください。

## 対応ファイル形式

- `.txt`
- `.md`
- `.html`

## Dev

ツールを読み込んで実行する場合

```sh
pip install -e .
wpctl post create article.md
```

## Tool

### Test

```sh
pip install -r requirements-dev.txt
pytest tests/
# ログを出力する場合
# pytest -s tests/
```

### Lint

```sh
pip install -r requirements-dev.txt
ruff check .
# 自動修正する場合
ruff check . --fix
```
