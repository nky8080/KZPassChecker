# 開発者向けドキュメント

*他の言語で読む: [English](DEVELOPMENT.md)*

このドキュメントは、文化の森お出かけパス施設休館情報エージェントプロジェクトの開発に参加する開発者向けの詳細な技術情報を提供します。

## 📋 目次

- [開発環境のセットアップ](#開発環境のセットアップ)
- [プロジェクト構造](#プロジェクト構造)
- [技術スタック](#技術スタック)
- [開発ワークフロー](#開発ワークフロー)
- [テスト戦略](#テスト戦略)
- [デバッグ方法](#デバッグ方法)
- [パフォーマンス最適化](#パフォーマンス最適化)
- [セキュリティ考慮事項](#セキュリティ考慮事項)
- [デプロイメント](#デプロイメント)

## 🛠️ 開発環境のセットアップ

### 前提条件

以下のソフトウェアがインストールされている必要があります：

- **Python 3.8以上** (推奨: 3.9+)
- **Git 2.0以上**
- **AWS CLI 2.0以上**
- **AgentCore CLI** (最新版)

### 詳細セットアップ手順

#### 1. リポジトリのクローンとセットアップ

```bash
# リポジトリをクローン
git clone <repository-url>
cd 文化の森お出かけパス施設休館情報エージェント

# 自動セットアップスクリプトを実行
python setup.py
```

#### 2. 手動セットアップ（詳細制御が必要な場合）

```bash
# 仮想環境の作成
python -m venv .venv

# 仮想環境のアクティベート
# Windows
.venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate

# 依存関係のインストール
pip install --upgrade pip
pip install -r requirements.txt

# 開発用依存関係のインストール（存在する場合）
pip install -r requirements-dev.txt
```

#### 3. AWS設定

```bash
# AWS CLIの設定
aws configure

# または環境変数で設定
export AWS_ACCESS_KEY_ID="your-access-key"
export AWS_SECRET_ACCESS_KEY="your-secret-key"
export AWS_DEFAULT_REGION="us-west-2"

# Bedrockモデルアクセスの確認
aws bedrock list-foundation-models --region us-west-2
```

#### 4. AgentCore設定

```bash
# AgentCore CLIのインストール確認
agentcore --version

# プロジェクトの設定
agentcore configure -e agent.py

# 設定の確認
agentcore status
```

### 開発用環境変数

開発時に使用する環境変数を`.env`ファイルに設定：

```bash
# .env ファイルの作成
cat > .env << EOF
# AWS設定
AWS_DEFAULT_REGION=us-west-2
AWS_ACCESS_KEY_ID=your-access-key
AWS_SECRET_ACCESS_KEY=your-secret-key

# AgentCore設定
BEDROCK_AGENTCORE_MEMORY_ID=your-memory-id

# 開発設定
LOG_LEVEL=DEBUG
REQUEST_TIMEOUT=30
DEBUG_MODE=true

# テスト設定
TEST_FACILITY=金沢21世紀美術館
TEST_DATE=2025-01-01
EOF
```

## 🏗️ プロジェクト構造

### ディレクトリ構成

```
文化の森お出かけパス施設休館情報エージェント/
├── agent.py                    # メインエージェント
├── facility_scraper.py         # スクレイピング機能
├── config.py                   # 設定管理
├── deploy.py                   # デプロイメント
├── setup.py                    # セットアップスクリプト
├── requirements.txt            # Python依存関係
├── .bedrock_agentcore.yaml     # AgentCore設定
├── Dockerfile                  # コンテナ設定
├── .env                        # 環境変数（開発用）
├── .gitignore                  # Git除外設定
├── README.md                   # プロジェクト説明
├── CONTRIBUTING.md             # 貢献ガイドライン
├── DEVELOPMENT.md              # このファイル
├── LICENSE                     # ライセンス
└── docs/                       # 追加ドキュメント
    ├── api.md                  # API仕様
    ├── architecture.md         # アーキテクチャ設計
    └── deployment.md           # デプロイメントガイド
```

### 主要ファイルの詳細

#### agent.py
- **役割**: メインのAgentCoreエージェント
- **主要機能**: 自然言語処理、施設情報取得、レスポンス生成
- **依存関係**: strands, facility_scraper, config

#### facility_scraper.py
- **役割**: 各施設の公式サイトからの情報取得
- **主要機能**: Webスクレイピング、データ解析、エラーハンドリング
- **依存関係**: requests, beautifulsoup4, config

#### config.py
- **役割**: 設定とデータの一元管理
- **主要機能**: 施設情報、AWS設定、スクレイピング設定
- **データ**: FACILITIES辞書、各種定数

## 🔧 技術スタック

### コア技術

- **Python 3.8+**: メイン開発言語
- **Amazon Bedrock**: Claude 3.7 Sonnetモデル
- **AgentCore**: Strands Agent Framework
- **BeautifulSoup4**: HTMLパースとスクレイピング
- **Requests**: HTTP通信

### 開発・運用技術

- **AWS CLI**: AWSサービス管理
- **Docker**: コンテナ化
- **Git**: バージョン管理
- **GitHub**: リポジトリホスティング

### 推奨開発ツール

```bash
# コードフォーマッター
pip install black

# リンター
pip install flake8 pylint

# 型チェッカー
pip install mypy

# テストフレームワーク
pip install pytest pytest-cov

# 開発用ユーティリティ
pip install ipython jupyter
```

## 🔄 開発ワークフロー

### 1. 機能開発の流れ

```bash
# 1. 最新のmainブランチを取得
git checkout main
git pull origin main

# 2. 機能ブランチを作成
git checkout -b feature/new-facility-support

# 3. 開発作業
# コードの変更、テストの追加

# 4. テストの実行
python -c "from agent import check_facility_closure; print('Test OK')"

# 5. コードフォーマット
black agent.py facility_scraper.py config.py

# 6. リンターチェック
flake8 agent.py facility_scraper.py config.py

# 7. 変更をコミット
git add .
git commit -m "feat: add support for new facility"

# 8. プッシュ
git push origin feature/new-facility-support

# 9. プルリクエスト作成
# GitHubでプルリクエストを作成
```

### 2. コミットメッセージ規約

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Type:**
- `feat`: 新機能
- `fix`: バグ修正
- `docs`: ドキュメント更新
- `style`: コードスタイル変更
- `refactor`: リファクタリング
- `test`: テスト追加・修正
- `chore`: その他の変更

**例:**
```
feat(scraper): add support for Kanazawa Noh Museum

- Add scraping logic for Kanazawa Noh Museum website
- Handle special holiday patterns for traditional arts venues
- Update facility configuration with new museum data

Closes #123
```

## 🧪 テスト戦略

### テストの種類

#### 1. 単体テスト

```python
# 基本機能のテスト
def test_facility_closure_basic():
    """基本的な施設休館情報取得のテスト"""
    from agent import check_facility_closure
    import json
    
    result = check_facility_closure('金沢21世紀美術館', '2025-01-01')
    data = json.loads(result)
    
    assert 'facility' in data
    assert 'date' in data
    assert 'is_closed' in data
    assert data['facility'] == '金沢21世紀美術館'

# スクレイピング機能のテスト
def test_scraper_functionality():
    """スクレイピング機能のテスト"""
    from facility_scraper import scrape_facility_info
    
    result = scrape_facility_info('金沢21世紀美術館', '2025-01-01')
    assert result is not None
    assert 'status' in result
```

#### 2. 統合テスト

```python
def test_end_to_end_workflow():
    """エンドツーエンドのワークフローテスト"""
    from agent import check_facility_closure
    from config import FACILITIES
    
    # 複数施設での動作確認
    test_facilities = ['金沢21世紀美術館', '石川県立美術館', '鈴木大拙館']
    
    for facility in test_facilities:
        result = check_facility_closure(facility, '明日')
        assert result is not None
        print(f"{facility}: テスト成功")
```

#### 3. パフォーマンステスト

```python
import time

def test_response_time():
    """レスポンス時間のテスト"""
    from agent import check_facility_closure
    
    start_time = time.time()
    result = check_facility_closure('金沢21世紀美術館', '2025-01-01')
    end_time = time.time()
    
    response_time = end_time - start_time
    assert response_time < 10.0  # 10秒以内
    print(f"レスポンス時間: {response_time:.2f}秒")
```

### テストの実行

```bash
# 基本テストの実行
python -c "
from agent import check_facility_closure
import json
result = check_facility_closure('金沢21世紀美術館', '2025-01-01')
data = json.loads(result)
print('基本テスト:', '成功' if 'facility' in data else '失敗')
"

# 複数施設テスト
python -c "
from config import FACILITIES
from agent import check_facility_closure
success_count = 0
total_count = min(5, len(FACILITIES))

for facility_name in list(FACILITIES.keys())[:total_count]:
    try:
        result = check_facility_closure(facility_name, '明日')
        if result:
            success_count += 1
            print(f'{facility_name}: 成功')
    except Exception as e:
        print(f'{facility_name}: 失敗 - {e}')

print(f'テスト結果: {success_count}/{total_count} 成功')
"

# パフォーマンステスト
python -c "
import time
from agent import check_facility_closure

start_time = time.time()
result = check_facility_closure('金沢21世紀美術館', '2025-01-01')
end_time = time.time()

print(f'レスポンス時間: {end_time - start_time:.2f}秒')
print('パフォーマンステスト:', '成功' if end_time - start_time < 10 else '失敗')
"
```

## 🐛 デバッグ方法

### ログレベルの設定

```python
import logging

# デバッグレベルのログを有効化
logging.basicConfig(level=logging.DEBUG)

# 環境変数での設定
import os
os.environ['LOG_LEVEL'] = 'DEBUG'
```

### デバッグ用コード

```python
# agent.py にデバッグ機能を追加
def debug_facility_closure(facility_name: str, date: str):
    """デバッグ用の詳細情報付き施設休館情報取得"""
    print(f"デバッグ: 施設名={facility_name}, 日付={date}")
    
    # スクレイピング結果の詳細表示
    from facility_scraper import scrape_facility_info
    scrape_result = scrape_facility_info(facility_name, date)
    print(f"スクレイピング結果: {scrape_result}")
    
    # 最終結果
    result = check_facility_closure(facility_name, date)
    print(f"最終結果: {result}")
    
    return result
```

### よくある問題とデバッグ方法

#### 1. AWS認証エラー

```bash
# 認証情報の確認
aws sts get-caller-identity

# 環境変数の確認
echo $AWS_ACCESS_KEY_ID
echo $AWS_SECRET_ACCESS_KEY
echo $AWS_DEFAULT_REGION
```

#### 2. スクレイピングエラー

```python
# 個別施設のスクレイピングテスト
from facility_scraper import scrape_facility_info
import json

facility = '金沢21世紀美術館'
date = '2025-01-01'

try:
    result = scrape_facility_info(facility, date)
    print(json.dumps(result, indent=2, ensure_ascii=False))
except Exception as e:
    print(f"エラー: {e}")
    import traceback
    traceback.print_exc()
```

#### 3. AgentCoreエラー

```bash
# AgentCoreログの確認
agentcore logs

# 設定の確認
agentcore status

# 再設定
agentcore configure -e agent.py
```

## ⚡ パフォーマンス最適化

### 1. レスポンス時間の最適化

```python
# 並行処理による高速化
import asyncio
import aiohttp

async def async_scrape_multiple_facilities(facilities, date):
    """複数施設の並行スクレイピング"""
    async with aiohttp.ClientSession() as session:
        tasks = []
        for facility in facilities:
            task = asyncio.create_task(
                async_scrape_facility(session, facility, date)
            )
            tasks.append(task)
        
        results = await asyncio.gather(*tasks)
        return results
```

### 2. キャッシュ機能

```python
from functools import lru_cache
import time

@lru_cache(maxsize=128)
def cached_facility_info(facility_name: str, date: str, cache_time: int):
    """キャッシュ機能付きの施設情報取得"""
    # cache_timeは時間単位のタイムスタンプ
    return scrape_facility_info(facility_name, date)

def get_cached_facility_info(facility_name: str, date: str):
    """1時間キャッシュの施設情報取得"""
    current_hour = int(time.time() // 3600)
    return cached_facility_info(facility_name, date, current_hour)
```

### 3. メモリ使用量の最適化

```python
# 大きなデータ構造の最適化
import sys

def optimize_facility_data():
    """施設データの最適化"""
    from config import FACILITIES
    
    # メモリ使用量の確認
    print(f"FACILITIES辞書のサイズ: {sys.getsizeof(FACILITIES)} bytes")
    
    # 不要なデータの削除
    optimized_facilities = {}
    for name, data in FACILITIES.items():
        optimized_facilities[name] = {
            'url': data['url'],
            'selector': data.get('selector', ''),
            'pattern': data.get('pattern', '')
        }
    
    return optimized_facilities
```

## 🔒 セキュリティ考慮事項

### 1. 機密情報の管理

```python
# 環境変数の使用
import os

# ❌ 悪い例: ハードコーディング
AWS_ACCESS_KEY = "AKIAIOSFODNN7EXAMPLE"

# ✅ 良い例: 環境変数の使用
AWS_ACCESS_KEY = os.environ.get('AWS_ACCESS_KEY_ID')
if not AWS_ACCESS_KEY:
    raise ValueError("AWS_ACCESS_KEY_ID environment variable is required")
```

### 2. 入力値の検証

```python
import re
from datetime import datetime

def validate_facility_name(facility_name: str) -> bool:
    """施設名の検証"""
    if not facility_name or len(facility_name) > 100:
        return False
    
    # 危険な文字の除外
    dangerous_chars = ['<', '>', '"', "'", '&', ';']
    return not any(char in facility_name for char in dangerous_chars)

def validate_date_format(date_str: str) -> bool:
    """日付形式の検証"""
    # YYYY-MM-DD形式の検証
    date_pattern = r'^\d{4}-\d{2}-\d{2}$'
    if re.match(date_pattern, date_str):
        try:
            datetime.strptime(date_str, '%Y-%m-%d')
            return True
        except ValueError:
            return False
    
    return False
```

### 3. HTTPリクエストのセキュリティ

```python
import requests
from urllib.parse import urlparse

def secure_http_request(url: str, timeout: int = 10) -> requests.Response:
    """セキュアなHTTPリクエスト"""
    # URLの検証
    parsed_url = urlparse(url)
    if parsed_url.scheme not in ['http', 'https']:
        raise ValueError("Invalid URL scheme")
    
    # セキュアなヘッダーの設定
    headers = {
        'User-Agent': 'Mozilla/5.0 (compatible; FacilityBot/1.0)',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'ja,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate',
        'Connection': 'keep-alive',
    }
    
    # リクエストの実行
    response = requests.get(
        url,
        headers=headers,
        timeout=timeout,
        allow_redirects=True,
        verify=True  # SSL証明書の検証
    )
    
    return response
```

## 🚀 デプロイメント

### ローカルテスト

```bash
# 仮想環境での動作確認
source .venv/bin/activate
python agent.py

# 基本機能テスト
python -c "from agent import check_facility_closure; print(check_facility_closure('金沢21世紀美術館', '2025-01-01'))"
```

### AgentCoreデプロイ

```bash
# 設定の確認
agentcore configure -e agent.py

# デプロイの実行
agentcore launch

# デプロイ状況の確認
agentcore status

# ログの確認
agentcore logs
```

### Dockerデプロイ

```bash
# Dockerイメージのビルド
docker build -t facility-closure-agent .

# コンテナの実行
docker run -e AWS_ACCESS_KEY_ID=$AWS_ACCESS_KEY_ID \
           -e AWS_SECRET_ACCESS_KEY=$AWS_SECRET_ACCESS_KEY \
           -e AWS_DEFAULT_REGION=us-west-2 \
           facility-closure-agent
```

### 本番環境での考慮事項

1. **環境変数の設定**: 本番用の認証情報
2. **ログレベル**: INFOまたはWARNING
3. **タイムアウト設定**: 適切なタイムアウト値
4. **エラーハンドリング**: 堅牢なエラー処理
5. **モニタリング**: ログとメトリクスの監視

## 📊 監視とメトリクス

### ログ設定

```python
import logging
import sys

def setup_logging():
    """ログ設定のセットアップ"""
    log_level = os.environ.get('LOG_LEVEL', 'INFO')
    
    logging.basicConfig(
        level=getattr(logging, log_level),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler('facility_agent.log')
        ]
    )
    
    return logging.getLogger(__name__)
```

### パフォーマンスメトリクス

```python
import time
from functools import wraps

def measure_performance(func):
    """パフォーマンス測定デコレータ"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        
        logger = logging.getLogger(__name__)
        logger.info(f"{func.__name__} executed in {end_time - start_time:.2f} seconds")
        
        return result
    return wrapper

@measure_performance
def check_facility_closure(facility_name: str, date: str) -> str:
    # 既存の実装
    pass
```

## 🔧 トラブルシューティング

### よくある問題と解決方法

#### 1. 依存関係の問題

```bash
# 依存関係の再インストール
pip uninstall -r requirements.txt -y
pip install -r requirements.txt

# 仮想環境の再作成
deactivate
rm -rf .venv
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

#### 2. AWS認証の問題

```bash
# 認証情報の確認
aws configure list
aws sts get-caller-identity

# 環境変数の設定
export AWS_ACCESS_KEY_ID="your-key"
export AWS_SECRET_ACCESS_KEY="your-secret"
export AWS_DEFAULT_REGION="us-west-2"
```

#### 3. スクレイピングの問題

```python
# 個別サイトのテスト
import requests
from bs4 import BeautifulSoup

def test_site_access(url):
    try:
        response = requests.get(url, timeout=10)
        print(f"Status: {response.status_code}")
        print(f"Content-Type: {response.headers.get('content-type')}")
        
        soup = BeautifulSoup(response.content, 'html.parser')
        print(f"Title: {soup.title.string if soup.title else 'No title'}")
        
    except Exception as e:
        print(f"Error: {e}")

# 使用例
test_site_access("https://www.kanazawa21.jp/")
```

## 📚 参考資料

### 公式ドキュメント

- [Amazon Bedrock Documentation](https://docs.aws.amazon.com/bedrock/)
- [AgentCore Documentation](https://docs.agentcore.aws.dev/)
- [Python Official Documentation](https://docs.python.org/3/)
- [BeautifulSoup Documentation](https://www.crummy.com/software/BeautifulSoup/bs4/doc/)

### 開発ツール

- [Black Code Formatter](https://black.readthedocs.io/)
- [Flake8 Linter](https://flake8.pycqa.org/)
- [MyPy Type Checker](https://mypy.readthedocs.io/)
- [Pytest Testing Framework](https://docs.pytest.org/)

### AWS関連

- [AWS CLI Configuration](https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-files.html)
- [IAM Best Practices](https://docs.aws.amazon.com/IAM/latest/UserGuide/best-practices.html)
- [Bedrock Model Access](https://docs.aws.amazon.com/bedrock/latest/userguide/model-access.html)

---

このドキュメントは継続的に更新されます。質問や改善提案がありましたら、GitHubのIssuesまたはDiscussionsでお知らせください。