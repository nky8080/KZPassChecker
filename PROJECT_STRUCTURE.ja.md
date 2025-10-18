# プロジェクト構造

*他の言語で読む: [English](PROJECT_STRUCTURE.md)*

## ディレクトリ構成

```
文化の森お出かけパス施設休館情報エージェント/
├── agent.py                    # メインのAgentCoreエージェント
├── facility_scraper.py         # 施設情報スクレイピング機能
├── config.py                   # 設定ファイル
├── deploy.py                   # デプロイメントスクリプト
├── setup.py                    # セットアップスクリプト
├── requirements.txt            # Python依存関係
├── .gitignore                  # Git除外設定
├── .bedrock_agentcore.yaml     # AgentCore設定
├── Dockerfile                  # Docker設定
├── README.md                   # プロジェクト説明
├── USAGE.md                    # 使用方法
└── PROJECT_STRUCTURE.md        # このファイル
```

## ファイル説明

### コアファイル
- **agent.py**: Amazon Bedrock AgentCore + Strands Agentを使用したメインエージェント
- **facility_scraper.py**: 18施設の公式サイトから休館情報を取得するスクレイピング機能
- **config.py**: 施設情報、AWS設定、スクレイピング設定を含む設定ファイル

### デプロイメント
- **deploy.py**: AWS AgentCoreへの自動デプロイスクリプト
- **setup.py**: ローカル開発環境のセットアップスクリプト
- **.bedrock_agentcore.yaml**: AgentCore設定ファイル
- **Dockerfile**: コンテナ化設定

### 設定・ドキュメント
- **requirements.txt**: Python依存関係（最適化済み）
- **.gitignore**: Git除外設定（Python開発用に最適化）
- **README.md**: プロジェクト概要と使用方法
- **USAGE.md**: 詳細な使用方法とAPI仕様

## 開発ワークフロー

1. **ローカル開発**: `python setup.py` でセットアップ
2. **テスト**: `python agent.py` でローカルテスト
3. **デプロイ**: `python deploy.py` でAWSデプロイ
4. **監視**: CloudWatchダッシュボードで監視

## ベストプラクティス準拠

- ✅ フラットな構造（AgentCoreアプリケーションに適している）
- ✅ 設定ファイルの分離
- ✅ 適切な.gitignore設定
- ✅ 依存関係の明確化
- ✅ ドキュメントの充実
- ✅ デプロイメント自動化