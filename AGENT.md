# AGENT ガイドライン

このドキュメントは、本リポジトリで動作する **AIエージェント（Cursor, ChatGPT など）向けの指示書**です。  
コード提案・自動修正・ドキュメント生成を行う際は、必ずこの内容に従ってください。

---

## 1. プロジェクト概要

- プロジェクト名: `TODO: プロジェクト名を書いてください`
- 主な用途: `TODO: このプロジェクトの目的を1〜3行で書く`
- 想定する利用者:
  - `例: 自分用のテンプレ / 小規模API / バッチスクリプト など`


## 2. 技術スタック & 環境

- 言語: Python 3.x（`TODO: 具体バージョンを書く: 例: 3.12`）
- 仮想環境: `.venv`（`python -m venv .venv`）
- パッケージ管理: `pip`（`requirements.txt` を利用）
- Linter / Formatter:
  - **Ruff**（Lint & Format 両方に使用）
- テスト: `pytest`（予定または導入済みなら）

### 環境のセットアップ

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```


### フォルダ構成

.
├── src/                   # メインのアプリケーションコード
├── tests/                 # テストコード
├── requirements.txt
├── ruff.toml
└── AGENT.md               # このファイル

エージェントは 原則として src/ 以下にコードを追加・修正してください。
設定ファイルやCI/CDは、既存の構成に従ってください。