# wpctl

WordPress APIを活用して、記事を投稿・管理するCLIツール。

## 概要

MarkDown / テキスト / HTMLファイルを読み込み、WordPress REST APIを通じて記事の投稿・更新を行います。

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
wpctl post create [-t "記事のタイトル"] <FilePath>
```

| 引数 | オプション | 必須 | 説明 |
| ---- | ---------- | ---- | ---- |
| `FilePath` | | true | 投稿するファイルのパス |
| `title` | `--title`, `-t` | | 記事タイトル（デフォルト: `タイトル未設定`）|

### 記事を更新する

```sh
wpctl post update --id <ID> [-t "記事のタイトル"] <FilePath>
```

| 引数 | オプション | 必須 | 説明 |
| ---- | ---------- | ---- | ---- |
| `FilePath` | | true | 投稿するファイルのパス |
| `id` | `--id` | true | 更新対象の記事ID |
| `title` | `--title`, `-t` | | 記事タイトル（デフォルト: `タイトル未設定`）|

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
