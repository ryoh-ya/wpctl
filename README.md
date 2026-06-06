# TODO:リポジトリ名


<ここにプロジェクトの説明を記載してください>


## Tool

### Test

テスト用のライブラリをインストールしてください。

```sh
pip install -r requirements-dev.txt
```

テストを実行する

```sh
pytest tests/
# ログを出力する場合
# pytest -s tests/
```

### Lint


```sh
pip install -r requirements-dev.txt
```

**lintを実行する方法**

```sh
ruff check .
```

例えば使われていない変数が存在する場合はなどは以下のように表示される

```log
F841 Local variable `x` is assigned to but never used
 --> src/main.py:7:5
  |
6 | def func_wrong():
7 |     x = 1 
  |     ^
  |
help: Remove assignment to unused variable `x`
```

**自動生成も実行する場合**

```sh
ruff check . --fix
```