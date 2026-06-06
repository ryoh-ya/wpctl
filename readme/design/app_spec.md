# アプリの仕様書

## エンドポイント周りの仕様

### ファイル構成

| ファイル                          | 役割                                                  |
| --------------------------------- | ----------------------------------------------------- |
| `src/wpctl/main.py`               | CLIエントリーポイント。引数パース・環境変数検証を行う |
| `src/wpctl/run.py`                | `run(args)` からロジック開始。コマンドを振り分ける    |
| `src/wpctl/api/api_wordpress.py`  | WordPress REST API クライアント                        |
| `src/wpctl/commands/create.py`    | 記事投稿コマンドのロジック                            |
| `src/wpctl/commands/update.py`    | 記事更新コマンドのロジック                            |
| `src/wpctl/libs/file_reader.py`   | ファイル読み込み・拡張子バリデーション                |
| `src/wpctl/libs/md_to_html.py`    | Markdown → HTML 変換・サニタイズ                      |

### 処理フロー

```
wpctl (CLI)
  └─ main() ─ 環境変数チェック(_validate_env)
       └─ run(args)
            └─ _run_post(args)
                 ├─ _run_post_create → commands/create.run()
                 │       ├─ libs/file_reader.read_file()
                 │       │      └─ libs/md_to_html.convert()  ※ .md のみ
                 │       └─ api/ApiWordpress.create_post()
                 └─ _run_post_update → commands/update.run()
                         ├─ libs/file_reader.read_file()
                         └─ api/ApiWordpress.update_post()
```

### 引数の内部名

`--id` オプションは argparse 内部では `post_id` として保持する（`id` は Python 組み込み関数と名前が衝突するため）。

## ファイル読み込み仕様

| 拡張子  | 処理                            |
| ------- | ------------------------------- |
| `.txt`  | そのまま API に渡す             |
| `.html` | そのまま API に渡す             |
| `.md`   | HTML 変換 → サニタイズして渡す  |

### Markdown サニタイズルール

- `<script>` タグは除去する
- `onerror`、`onclick` 等のイベント属性は除去する
- 許可する属性: `a[href, title, target]`、`img[src, alt, width, height]` など

## エラーハンドリング仕様

| エラー種別                | 発生箇所              | 動作                                         |
| ------------------------- | --------------------- | -------------------------------------------- |
| 必須環境変数が未設定      | `main._validate_env`  | エラーメッセージを stderr に出力して exit(1) |
| ファイルが存在しない      | `libs.file_reader`    | `FileReadError` を raise → run.py で exit(1) |
| 未対応のファイル拡張子    | `libs.file_reader`    | `FileReadError` を raise → run.py で exit(1) |
| WordPress API HTTP エラー | `api.ApiWordpress`    | `WordPressAPIError` を raise → run.py で exit(1) |
