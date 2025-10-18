# Design Document

## Overview

GitHub公開準備プロジェクトは、現在の開発用プロジェクトを本番公開可能な状態に整理・最適化することを目的とします。プロジェクトには100以上のファイルが含まれており、その大部分は開発・テスト・デバッグ用の一時的なファイルです。これらを適切に整理し、セキュリティ対策を施し、ドキュメントを充実させて、プロフェッショナルなオープンソースプロジェクトとして公開できる状態にします。

## Architecture

### ファイル分類システム
プロジェクト内のファイルを以下のカテゴリに分類します：

1. **コアファイル（保持）**
   - `agent.py`: メインのAgentCoreエージェント
   - `facility_scraper.py`: 施設情報スクレイピング機能
   - `config.py`: 設定ファイル
   - `deploy.py`: デプロイメント機能
   - `setup.py`: パッケージセットアップ

2. **設定・ドキュメントファイル（更新）**
   - `README.md`: プロジェクト説明（大幅更新）
   - `requirements.txt`: 依存関係（レビュー・最適化）
   - `.bedrock_agentcore.yaml`: AgentCore設定

3. **削除対象ファイル**
   - テストファイル（`test_*.py`）
   - デバッグファイル（`debug_*.py`）
   - 分析ファイル（`analyze_*.py`）
   - 一時的な結果ファイル（`.json`, `.png`, `.pdf`, `.txt`）
   - その他の開発用ファイル

### セキュリティレビューシステム
1. **機密情報スキャン**: APIキー、パスワード、認証情報の検出
2. **設定ファイルレビュー**: 環境変数の使用確認
3. **`.gitignore`作成**: 機密ファイルの除外設定

## Components and Interfaces

### 1. ファイルクリーンアップコンポーネント
```
FileCleanup
├── identify_files_to_remove()
├── categorize_files()
├── safe_file_removal()
└── verify_core_functionality()
```

### 2. セキュリティレビューコンポーネント
```
SecurityReview
├── scan_for_secrets()
├── review_configuration()
├── create_gitignore()
└── validate_security_measures()
```

### 3. ドキュメント生成コンポーネント
```
DocumentationGenerator
├── update_readme()
├── create_contributing_guide()
├── add_license_file()
└── optimize_requirements()
```

### 4. プロジェクト構造最適化コンポーネント
```
ProjectOptimizer
├── organize_directory_structure()
├── consolidate_functionality()
├── optimize_repository_size()
└── validate_final_structure()
```

## Data Models

### ファイル分類モデル
```python
class FileCategory:
    CORE = "core"           # 保持必須
    CONFIG = "config"       # 更新対象
    DOCUMENTATION = "docs"  # 更新対象
    TEMPORARY = "temp"      # 削除対象
    TEST = "test"          # 削除対象
    DEBUG = "debug"        # 削除対象
```

### クリーンアップ結果モデル
```python
class CleanupResult:
    files_removed: List[str]
    files_kept: List[str]
    files_updated: List[str]
    security_issues: List[str]
    recommendations: List[str]
```

## Error Handling

### ファイル操作エラー
- ファイル削除失敗時のロールバック機能
- 重要ファイルの誤削除防止チェック
- バックアップ作成による安全な操作

### セキュリティチェックエラー
- 機密情報検出時の警告表示
- 設定ファイルの検証失敗時の修正提案
- 不完全なセキュリティ対策の検出

### ドキュメント生成エラー
- テンプレート読み込み失敗時の代替処理
- 不正なマークダウン形式の修正
- 依存関係解析失敗時の手動確認要求

## Testing Strategy

### 1. ファイル分類テスト
- 各ファイルが正しいカテゴリに分類されることを確認
- 重要ファイルが誤って削除対象にならないことを検証
- パターンマッチングの精度テスト

### 2. セキュリティテスト
- 機密情報検出の精度テスト
- `.gitignore`の効果確認
- 設定ファイルの安全性検証

### 3. ドキュメント品質テスト
- README.mdの完全性確認
- マークダウン形式の正確性検証
- リンクの有効性チェック

### 4. 統合テスト
- クリーンアップ後のプロジェクト動作確認
- 依存関係の整合性テスト
- デプロイメント機能の動作確認

## Implementation Phases

### Phase 1: 分析・計画
1. 現在のファイル構造の完全な分析
2. 削除対象ファイルの特定
3. セキュリティリスクの評価

### Phase 2: クリーンアップ
1. 安全なファイル削除の実行
2. ディレクトリ構造の最適化
3. 重複機能の統合

### Phase 3: セキュリティ対策
1. 機密情報の除去・保護
2. `.gitignore`の作成
3. 設定ファイルの最適化

### Phase 4: ドキュメント整備
1. README.mdの全面更新
2. ライセンスファイルの追加
3. 貢献ガイドラインの作成

### Phase 5: 最終検証
1. プロジェクト全体の動作確認
2. セキュリティチェックの実行
3. 公開準備の最終確認

## Performance Considerations

- 大量ファイル削除時のシステム負荷管理
- リポジトリサイズの最適化
- ドキュメント生成の効率化
- セキュリティスキャンの高速化

## Deployment Strategy

1. **ローカル環境での作業完了**
2. **新しいGitリポジトリの初期化**
3. **クリーンなファイルセットのコミット**
4. **GitHubへのプッシュ**
5. **リポジトリ設定の最適化**