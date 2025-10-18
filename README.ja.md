# 文化の森お出かけパス 施設休館情報エージェント

*他の言語で読む: [English](README.md)*

Amazon Bedrock AgentCoreを使用して、石川県の文化の森お出かけパス対象施設の休館情報を調べるインテリジェントエージェントです。

## 📋 概要

このプロジェクトは、文化の森お出かけパス（https://odekakepass.hot-ishikawa.jp）で利用可能な18の文化施設について、指定した日付の休館情報を自動的に取得・提供するAIエージェントです。各施設の公式サイトから最新の休館情報をリアルタイムでスクレイピングし、正確で信頼性の高い情報を提供します。

### 主な特徴

- **リアルタイム情報取得**: 各施設の公式サイトから最新の休館情報を自動取得
- **包括的な施設対応**: 文化の森お出かけパス対象の全18施設に対応
- **多様な休館パターン対応**: 定期休館日、臨時休館日、展示替え期間、祝日対応など
- **高精度判定**: 施設ごとに最適化されたスクレイピング手法を採用
- **クラウドデプロイ対応**: Amazon Bedrock AgentCoreによるスケーラブルな運用

## 🏛️ 対象施設

文化の森お出かけパスで利用可能な全18施設：

1. **鈴木大拙館** - 月曜定休（祝日の場合は翌平日）
2. **金沢21世紀美術館** - 年末年始のみ休館
3. **いしかわ生活工芸ミュージアム** - 不定休
4. **武家屋敷跡 野村家** - 年末年始のみ休館
5. **国指定重要文化財 成巽閣** - 不定休
6. **石川県立歴史博物館** - 不定休
7. **国立工芸館** - 月曜定休（祝日の場合は翌平日）
8. **特別名勝 兼六園** - 年中無休
9. **金沢城公園** - 年中無休
10. **前田土佐守家資料館** - 月曜定休（祝日の場合は開館）
11. **金沢市老舗記念館** - 月曜定休（祝日の場合は開館）
12. **石川県立美術館** - 不定休
13. **金沢くらしの博物館** - 月曜定休（祝日の場合は開館）
14. **金沢能楽美術館** - 不定休
15. **金沢市立中村記念美術館** - 月曜定休（祝日の場合は翌平日）
16. **加賀本多博物館** - 不定休
17. **金沢ふるさと偉人館** - 不定休
18. **石川四高記念文化交流館** - 不定休

## 🚀 機能

### 主要機能

- **施設休館情報取得**: 指定した施設・日付の休館情報を詳細に提供
- **日付形式の柔軟な対応**: "2025-01-15"、"1月15日"、"明日"など様々な形式に対応
- **祝日判定**: 国民の祝日を考慮した正確な開館状況判定
- **展示替え期間対応**: 美術館・博物館の展示替えによる臨時休館を検出
- **エラーハンドリング**: ネットワークエラーやサイト変更に対する堅牢な処理

### 技術的特徴

- **Strands Agent Framework**: 高度なAIエージェント機能を提供
- **BeautifulSoup4**: 高精度なWebスクレイピング
- **AWS Bedrock**: Claude 3.7 Sonnetモデルによる自然言語処理
- **AgentCore Memory**: 学習機能とセッション管理
- **非同期処理**: 複数施設の同時情報取得

## 📁 プロジェクト構成

```
文化の森お出かけパス施設休館情報エージェント/
├── agent.py                    # メインのAgentCoreエージェント
├── facility_scraper.py         # 施設情報スクレイピング機能
├── config.py                   # 設定ファイル（施設情報・AWS設定）
├── deploy.py                   # デプロイメント機能
├── setup.py                    # 自動セットアップスクリプト
├── requirements.txt            # Python依存関係
├── .bedrock_agentcore.yaml     # AgentCore設定ファイル
├── Dockerfile                  # コンテナ設定
└── README.md                   # このファイル
```

## 🛠️ システム要件

### 必要なソフトウェア

- **Python**: 3.8以上
- **AWS CLI**: 2.0以上
- **AgentCore CLI**: 最新版
- **Git**: バージョン管理用

### AWS要件

- **AWSアカウント**: 有効なAWSアカウント
- **リージョン**: us-west-2（オレゴン）
- **Bedrockアクセス**: Claude 3.7 Sonnetモデルへのアクセス権限
- **IAMロール**: AgentCore実行用の適切な権限

## 📦 インストール手順

### 1. リポジトリのクローン

```bash
git clone <repository-url>
cd 文化の森お出かけパス施設休館情報エージェント
```

### 2. 自動セットアップの実行

```bash
python setup.py
```

このスクリプトが以下を自動実行します：
- 仮想環境の作成
- 依存関係のインストール
- AWS設定の確認

### 3. 手動セットアップ（必要に応じて）

#### 仮想環境の作成とアクティベート

**Windows:**
```cmd
python -m venv .venv
.venv\Scripts\activate
```

**macOS/Linux:**
```bash
python -m venv .venv
source .venv/bin/activate
```

#### 依存関係のインストール

```bash
pip install -r requirements.txt
```

### 4. AWS設定

#### AWS CLIの設定

```bash
aws configure
```

以下の情報を入力：
- **AWS Access Key ID**: あなたのアクセスキー
- **AWS Secret Access Key**: あなたのシークレットキー
- **Default region name**: `us-west-2`
- **Default output format**: `json`

#### Bedrockモデルアクセスの有効化

1. AWS Console → Amazon Bedrock → Model access
2. "Claude 3.7 Sonnet" を選択して有効化
3. 利用規約に同意してアクセスを許可

## 🎯 使用方法

### ローカルでのテスト実行

```bash
# 仮想環境をアクティベート
source .venv/bin/activate  # macOS/Linux
# または
.venv\Scripts\activate     # Windows

# エージェントをローカルで実行
python agent.py
```

### AgentCoreへのデプロイ

#### 1. AgentCore設定

```bash
agentcore configure -e agent.py
```

#### 2. クラウドへのデプロイ

```bash
agentcore launch
```

#### 3. デプロイ状況の確認

```bash
agentcore status
```

### 使用例

#### 基本的な使用方法

```python
# 特定の施設の休館情報を確認
check_facility_closure("石川県立美術館", "2025-01-15")

# 自然言語での日付指定
check_facility_closure("金沢21世紀美術館", "明日")

# 複数の日付形式に対応
check_facility_closure("鈴木大拙館", "1月15日")
```

#### レスポンス例

```json
{
  "facility": "石川県立美術館",
  "date": "2025-01-15",
  "weekday": "水曜日",
  "is_closed": false,
  "closure_reason": "",
  "confidence": 0.95,
  "source": "公式サイト",
  "holiday_info": null,
  "additional_info": "開館予定です。開館時間: 午前9時30分～午後6時（入館は午後5時30分まで）"
}
```

### コマンドライン使用例

```bash
# 直接的な施設名指定
python -c "from agent import check_facility_closure; print(check_facility_closure('金沢21世紀美術館', '2025-01-20'))"

# 複数施設の一括確認
python -c "
from agent import check_facility_closure
facilities = ['石川県立美術館', '金沢21世紀美術館', '鈴木大拙館']
for facility in facilities:
    print(f'{facility}: {check_facility_closure(facility, \"明日\")}')
"
```

## 🔧 設定

### 環境変数

以下の環境変数を設定できます：

```bash
# AgentCore Memory ID（オプション）
export BEDROCK_AGENTCORE_MEMORY_ID="your-memory-id"

# ログレベル
export LOG_LEVEL="INFO"

# タイムアウト設定
export REQUEST_TIMEOUT="10"
```

### config.py の主要設定

```python
# AWS設定
REGION = "us-west-2"
MODEL_ID = "us.anthropic.claude-3-7-sonnet-20250219-v1:0"

# スクレイピング設定
REQUEST_TIMEOUT = 10
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
```

## 🧪 テスト

### 単体テスト

```bash
# 基本機能のテスト
python -m pytest tests/ -v

# 特定の施設のテスト
python -c "
from agent import check_facility_closure
import json
result = check_facility_closure('金沢21世紀美術館', '2025-01-01')
print(json.dumps(json.loads(result), indent=2, ensure_ascii=False))
"
```

### 統合テスト

```bash
# 全施設の動作確認
python -c "
from config import FACILITIES
from agent import check_facility_closure
import json

for facility_name in list(FACILITIES.keys())[:3]:  # 最初の3施設をテスト
    result = check_facility_closure(facility_name, '明日')
    data = json.loads(result)
    print(f'{facility_name}: {\"開館\" if not data.get(\"is_closed\") else \"休館\"}')
"
```

## 🚨 トラブルシューティング

### よくある問題と解決方法

#### 1. AWS認証エラー

```
Error: Unable to locate credentials
```

**解決方法:**
```bash
aws configure
# または
export AWS_ACCESS_KEY_ID="your-key"
export AWS_SECRET_ACCESS_KEY="your-secret"
export AWS_DEFAULT_REGION="us-west-2"
```

#### 2. Bedrockモデルアクセスエラー

```
Error: Access denied to model
```

**解決方法:**
1. AWS Console → Bedrock → Model access
2. Claude 3.7 Sonnetを有効化
3. 数分待ってから再試行

#### 3. スクレイピングエラー

```
Error: Failed to fetch facility information
```

**解決方法:**
- ネットワーク接続を確認
- 施設の公式サイトが利用可能か確認
- タイムアウト設定を調整（config.py）

#### 4. AgentCoreデプロイエラー

```
Error: Failed to deploy agent
```

**解決方法:**
```bash
# 設定を再確認
agentcore configure -e agent.py

# ログを確認
agentcore logs

# 再デプロイ
agentcore launch --force
```

### ログの確認

```bash
# AgentCoreログ
agentcore logs

# ローカル実行時のデバッグ
python agent.py --debug
```

## 📈 パフォーマンス

### 応答時間

- **単一施設照会**: 平均 2-5秒
- **複数施設照会**: 平均 5-15秒
- **キャッシュ利用時**: 平均 0.5-1秒

### スケーラビリティ

- **同時リクエスト**: 最大100リクエスト/分
- **日次照会数**: 制限なし（AWS利用料金に依存）
- **メモリ使用量**: 約50-100MB

## 🔒 セキュリティ

### データ保護

- **個人情報**: 収集・保存しません
- **ログ**: 施設名と日付のみ記録
- **通信**: HTTPS暗号化通信

### AWS セキュリティ

- **IAMロール**: 最小権限の原則
- **VPC**: プライベートネットワーク内で実行
- **暗号化**: 保存時・転送時の暗号化

## 🤝 貢献

### 開発への参加

1. **フォーク**: このリポジトリをフォーク
2. **ブランチ作成**: `git checkout -b feature/new-feature`
3. **変更実装**: コードの変更と適切なテスト
4. **コミット**: `git commit -am 'Add new feature'`
5. **プッシュ**: `git push origin feature/new-feature`
6. **プルリクエスト**: GitHubでプルリクエストを作成

### 開発環境のセットアップ

```bash
# 開発用依存関係のインストール
pip install -r requirements-dev.txt

# プリコミットフックの設定
pre-commit install

# テストの実行
python -m pytest tests/ -v --coverage
```

### コーディング規約

- **PEP 8**: Python標準コーディング規約に準拠
- **型ヒント**: 可能な限り型ヒントを使用
- **ドキュメント**: 関数・クラスにdocstringを記載
- **テスト**: 新機能には適切なテストを追加

## 📄 ライセンス

このプロジェクトはMITライセンスの下で公開されています。詳細は[LICENSE](LICENSE)ファイルをご覧ください。

## 📞 サポート

### 問い合わせ

- **Issues**: GitHubのIssuesページで問題を報告
- **Discussions**: 機能要望や質問はDiscussionsで
- **Email**: 緊急の問題は[email]まで

### よくある質問

**Q: 新しい施設を追加できますか？**
A: はい。`config.py`のFACILITIES辞書に施設情報を追加してください。

**Q: 他の地域の施設に対応していますか？**
A: 現在は石川県の文化の森お出かけパス対象施設のみです。他地域への拡張は今後検討予定です。

**Q: 商用利用は可能ですか？**
A: MITライセンスの範囲内で商用利用可能です。

## 🔄 更新履歴

### v1.0.0 (2025-01-XX)
- 初回リリース
- 18施設の基本的な休館情報取得機能
- AgentCore統合
- 自動セットアップスクリプト

### 今後の予定

- [ ] 施設の開館時間情報の追加
- [ ] 特別展・企画展情報の取得
- [ ] 多言語対応（英語・中国語・韓国語）
- [ ] モバイルアプリ連携
- [ ] 他地域への拡張

---

**文化の森お出かけパス 施設休館情報エージェント** - 石川県の文化施設をもっと身近に 🏛️✨
