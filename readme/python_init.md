# Python Project

- [Python Project](#python-project)
  - [仮想環境を構築する](#仮想環境を構築する)
    - [venvで構築する](#venvで構築する)
    - [uvで構築する](#uvで構築する)
  - [Linter](#linter)
    - [ruffライブラリの場合](#ruffライブラリの場合)
  - [Doc](#doc)
    - [クラス図を生成したい場合](#クラス図を生成したい場合)
  - [Secure](#secure)
    - [ツール: pip-audit](#ツール-pip-audit)
    - [ツール: safety](#ツール-safety)
  - [Release](#release)
    - [PyPI](#pypi)
      - [pyproject.tomlの記載方法](#pyprojecttomlの記載方法)
  - [Git公開時のセキュリティチェック](#git公開時のセキュリティチェック)
    - [gitleaks](#gitleaks)
    - [trufflehog](#trufflehog)
    - [Githubと連携](#githubと連携)
      - [スナップショットにしてGithubに配布する場合](#スナップショットにしてgithubに配布する場合)

## 仮想環境を構築する

### venvで構築する

```sh
python3 -m venv .venv
# Linux 
source .venv/bin/activate
# Windows
# .venv/Scripts/activate

pip install -r requirements.txt
# For Develop(Tests,Docs)
pip install -r requirements-dev.txt
```

### uvで構築する

プロジェクトを生成する場合

```bash
uv init <ProjectName>
# --pythonまたは-pにバージョンを指定できます
# uv init <ProjectName> -p 3.10とすると">=3.10,<3.11"となる
```

同期する場合

```sh
uv sync
```

## Linter

### ruffライブラリの場合

RuffFlake8 のルールを多数サポートしています。
ruff.tomlで設定できます


```toml
select = ["E", "W"] 
line-length = 88
```


| 分類 | コード | 内容                                |
| ---- | ------ | ----------------------------------- |
| W    | W291   | 末尾スペース（trailing whitespace） |
|      | W293   | ファイル末尾の空行の空白            |
| E    | E303   | 空行が多すぎる                      |
|      | E501   | 行が長すぎる                        |


リンターを実行する場合

```sh
# プロジェクト全体のPythonファイルを確認する
ruff check .
# ソースコードのみ実行する場合
ruff check src
# 修正を実行する場合
ruff check . --fix
```

**レポートを生成する場合**

シンプルなレポートとしては`generate_linter.sh`を実行してください

```sh
sh scripts/generate_linter.sh
```

形式を指定して出力する方法

```sh
ruff check . --output-format json --output-file ruff-report.json
```

`--output-file`は`github`など様々な形式が指定できます

コメントを生成する方法を検討が必要

## Doc

初期設定を行う

```sh
mkdir docs 
cd  docs 
sphinx-quickstart
```

rstファイルを自動生成する

```sh
cd  docs 
sphinx-apidoc -o . ../src
```


Docsを自動生成する

```
cd docs
make html
```

### クラス図を生成したい場合

**前提条件**:
* OSにgraphvizが必要になります。 

Linux / Mac

```sh
# Linux
sudo apt-get install -y graphviz
# Mac
brew install graphviz
# 確認する
dot -V
```


**クラス図の作成方法**

`pyreverse`を使用してクラス図を生成する
pyreverseはpylintパッケージに含まれています

```sh
pyreverse -o png -p projectName ./src
```

ひとつのファイルの実行する場合

```sh
pyreverse -o png -p Example src/example.py
```

注) pyreverse自体には出力先を直接指定するオプションはありません mvコマンドで実行する


## Secure

### ツール: pip-audit

ライブラリの脆弱性を確認する

```sh
pip install pip-audit
```

実行する方法

```sh
# インストール済み依存を全てスキャン
pip-audit
# requirements.txt を直接スキャン
pip-audit -r requirements.txt --desc
# tomlもスキャンできます
pip-audit -r pyproject.toml
```

* `--desc`: 説明付き

JSONで結果を出力する場合

```sh
pip-audit -f json -o pip-audit-report.json
```

Markdownで出力する場合

```sh
pip-audit -f markdown
```


### ツール: safety

* github: https://github.com/pyupio/safety
* Safety DBを使用し脆弱性のチェックを行う


```sh
pip install safety
```

実行する方法

```sh
safety check -r requirements.txt
```

## Release

タグを追加する処理

```sh
git checkout release/x.y.z
git pull
git tag -a vX.Y.Z -m "Release vX.Y.Z"
git push origin vX.Y.Z
```

### PyPI

1. [PyPIアカウント作成](https://pypi.org/account/register/)
   1. 2FAが必要です
2. APIトークン発行
   1. PyPI → Account settings
   2. `API tokens`
   3. `「Add API token」`
3. パッケージ構成を用意 (pyproject.toml)
4. ビルド (wheel / sdist)
   1. `pip install build twine`: インストールを実行する
   2. `python -m build`: ビルドする
5. twineでアップロード
   1. `twine upload dist/*`
6. PyPI上で確認
   1. `https://pypi.org/project/<PKG_NAME>/`: パッケージの確認
   2. `pip install <PKG_NAME>`: インストールの確認


テスト用PyPI(本番前に実行する)

```sh
twine upload --repository testpypi dist/*
pip install -i https://test.pypi.org/simple <PKG_NAME>
```

#### pyproject.tomlの記載方法

```tml
[build-system]
requires = ["setuptools>=69", "wheel"]
build-backend = "setuptools.build_meta"
```


## Git公開時のセキュリティチェック

### gitleaks

```sh
brew install gitleaks
```

バイナリ(CL/サーバ)

```sh
curl -sSL https://github.com/gitleaks/gitleaks/releases/latest/download/gitleaks-linux-amd64 -o gitleaks
chmod +x gitleaks
```

インストール確認

```sh
gitleaks version
```

実際に使用してみる

```sh
gitleaks detect --source .
# レポート出力する
gitleaks detect --source . --report-format json --report-path gitleaks.json
```

### trufflehog

履歴までスキャンできるツールです。

* Git履歴を最初のコミットから全探索
* 過去に漏らしたかもしれない不安がある
* 処理は重く時間がかかる
  
**インストールの場合**

```sh
# Mac
brew install trufflehog
# pip
pip install trufflehog
```

**実行方法**

```sh
trufflehog git file://$(pwd) --only-verified
```

### Githubと連携

```sh
git remote add ithub https://github.com/XXX/YYY.git
```

#### スナップショットにしてGithubに配布する場合

```sh
export BRANCH="release" # distribution etc...
export REMOTE="origin" # github etc...

# orphan ブランチ作成
git checkout --orphan "$BRANCH"
# 既存ファイルを全部ステージから外して消す
git rm -rf .
# ファイル配置
git add .
# コミット
git commit -m "Snapshot Vx.x.x"
# GitHubにpush
git push "$REMOTE" "$TARGET_BRANCH" --force
```



