# アプリの仕様書

## エンドポイント周りの詳細

### ファイル構成

| ファイル            | 役割                                                   |
| ------------------- | ------------------------------------------------------ |
| `src/wpctl/main.py` | CLIエントリーポイント。引数パース・ロガー初期化を行う  |
| `src/wpctl/run.py`  | `run(args)` からロジックを開始。コマンドを振り分ける   |

### 処理フロー

```
wpctl (CLI) → main() → run(args) → _run_post(args) → _run_post_create / _run_post_update
```

### 引数の内部名

`--id` オプションは argparse 内部では `post_id` として保持する（`id` は Python 組み込み関数と名前が衝突するため）。

