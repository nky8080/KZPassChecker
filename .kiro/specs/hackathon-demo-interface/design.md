# Design Document

## Overview

金沢文化施設エージェントの動作確認用デモ画面は、S3でホストされる静的HTMLページとして実装されます。利用者がブラウザから直接アクセスし、エージェントの機能を簡単に試せる環境を提供します。シンプルで直感的なインターフェースを通じて、エージェントの価値を迅速に理解できるよう設計されています。

## Architecture

### システム構成

```
[利用者のブラウザ] 
    ↓ HTTPS
[S3 Static Website] 
    ↓ API Gateway/Lambda
[Amazon Bedrock AgentCore]
    ↓ 
[文化施設エージェント]
```

### 主要コンポーネント

1. **フロントエンド (S3 Static Website)**
   - 単一のHTMLファイル
   - CSS（インライン or 外部ファイル）
   - JavaScript（バニラJS、ライブラリ依存なし）

2. **API層**
   - API Gateway + Lambda（エージェント呼び出し用）
   - CORS設定でS3からのアクセスを許可

3. **エージェント層**
   - 既存のAmazon Bedrock AgentCore
   - 既存の文化施設エージェント

## Components and Interfaces

### フロントエンドコンポーネント

#### 1. メインインターフェース
```html
<div class="demo-container">
  <header class="demo-header">
    <h1>金沢文化施設 休館情報エージェント</h1>
    <p>施設の休館情報を簡単に確認できます</p>
  </header>
  
  <main class="demo-main">
    <div class="query-section">
      <textarea id="queryInput" placeholder="質問を入力してください..."></textarea>
      <button id="submitBtn">質問する</button>
    </div>
    
    <div class="examples-section">
      <h3>使用例</h3>
      <div class="example-buttons">
        <!-- サンプル質問ボタン -->
      </div>
    </div>
    
    <div class="response-section">
      <div id="loadingIndicator" class="hidden">
        <div class="spinner"></div>
        <p>施設情報を取得しています...</p>
      </div>
      <div id="responseContent"></div>
    </div>
  </main>
</div>
```

#### 2. サンプル質問コンポーネント
```javascript
const sampleQueries = [
  "21世紀美術館は12月25日に開いていますか？",
  "来週の月曜日に開いている施設はどこですか？",
  "兼六園の今日の開園状況を教えてください",
  "Is the 21st Century Museum open on December 25th?",
  "Which facilities are open next Monday?"
];
```

#### 3. ローディング表示コンポーネント
```css
.spinner {
  border: 4px solid #f3f3f3;
  border-top: 4px solid #3498db;
  border-radius: 50%;
  width: 40px;
  height: 40px;
  animation: spin 2s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}
```

### API インターフェース

#### エージェント呼び出しAPI
```javascript
// POST /api/query
{
  "query": "21世紀美術館は12月25日に開いていますか？"
}

// Response
{
  "response": "21世紀美術館は12月25日（月曜日）も開館しています...",
  "responseTime": 2.3,
  "timestamp": "2024-12-20T10:30:00Z"
}
```

## Data Models

### リクエストモデル
```typescript
interface QueryRequest {
  query: string;
  timestamp?: string;
}
```

### レスポンスモデル
```typescript
interface QueryResponse {
  response: string;
  responseTime: number;
  timestamp: string;
  error?: string;
}
```

### UIステートモデル
```typescript
interface UIState {
  isLoading: boolean;
  currentQuery: string;
  lastResponse: QueryResponse | null;
  error: string | null;
}
```

## Error Handling

### エラータイプと対応

#### 1. ネットワークエラー
```javascript
function handleNetworkError(error) {
  showError("ネットワークエラーが発生しました。インターネット接続を確認してください。");
}
```

#### 2. API エラー
```javascript
function handleAPIError(status, message) {
  switch(status) {
    case 429:
      showError("リクエストが多すぎます。しばらく待ってから再試行してください。");
      break;
    case 500:
      showError("サーバーエラーが発生しました。しばらく待ってから再試行してください。");
      break;
    default:
      showError(`エラーが発生しました: ${message}`);
  }
}
```

#### 3. タイムアウトエラー
```javascript
const TIMEOUT_MS = 30000; // 30秒

function queryWithTimeout(query) {
  return Promise.race([
    fetchAgentResponse(query),
    new Promise((_, reject) => 
      setTimeout(() => reject(new Error('Timeout')), TIMEOUT_MS)
    )
  ]);
}
```

### エラー表示UI
```html
<div id="errorMessage" class="error-message hidden">
  <span class="error-icon">⚠️</span>
  <span class="error-text"></span>
  <button class="error-close" onclick="hideError()">×</button>
</div>
```

## Testing Strategy

### 手動テスト項目

#### 1. 基本機能テスト
- [ ] ページの正常な読み込み
- [ ] 質問入力と送信
- [ ] サンプル質問ボタンの動作
- [ ] レスポンス表示の確認

#### 2. エラーハンドリングテスト
- [ ] ネットワーク切断時の動作
- [ ] 無効な入力に対する応答
- [ ] タイムアウト時の動作

#### 3. ユーザビリティテスト
- [ ] 日本語・英語質問の動作確認
- [ ] 長い質問文の処理
- [ ] 連続質問の動作

#### 4. パフォーマンステスト
- [ ] 初回読み込み時間
- [ ] API応答時間の表示
- [ ] 大きなレスポンスの表示

### 自動テスト（オプション）
```javascript
// 基本的なJavaScriptテスト
function testSampleQueryExecution() {
  const button = document.querySelector('.example-button');
  button.click();
  const input = document.getElementById('queryInput');
  assert(input.value.length > 0, "Sample query should populate input");
}
```

## Deployment Architecture

### S3 Static Website設定
```json
{
  "IndexDocument": {
    "Suffix": "index.html"
  },
  "ErrorDocument": {
    "Key": "error.html"
  }
}
```

### CloudFront設定（オプション）
```json
{
  "Origins": [{
    "DomainName": "demo-bucket.s3.amazonaws.com",
    "OriginPath": "",
    "CustomOriginConfig": {
      "HTTPPort": 80,
      "HTTPSPort": 443,
      "OriginProtocolPolicy": "https-only"
    }
  }],
  "DefaultCacheBehavior": {
    "TargetOriginId": "S3-demo-bucket",
    "ViewerProtocolPolicy": "redirect-to-https"
  }
}
```

### API Gateway設定
```yaml
paths:
  /query:
    post:
      summary: Query the cultural facility agent
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              properties:
                query:
                  type: string
      responses:
        200:
          description: Successful response
          content:
            application/json:
              schema:
                type: object
                properties:
                  response:
                    type: string
                  responseTime:
                    type: number
                  timestamp:
                    type: string
```

## Security Considerations

### CORS設定
```javascript
// API Gateway CORS設定
{
  "Access-Control-Allow-Origin": "https://your-demo-domain.com",
  "Access-Control-Allow-Methods": "POST, OPTIONS",
  "Access-Control-Allow-Headers": "Content-Type"
}
```

### レート制限
```javascript
// Lambda関数でのレート制限
const rateLimiter = {
  maxRequests: 10,
  windowMs: 60000, // 1分
  message: "Too many requests, please try again later."
};
```

### 入力検証
```javascript
function validateQuery(query) {
  if (!query || query.trim().length === 0) {
    throw new Error("質問を入力してください");
  }
  if (query.length > 1000) {
    throw new Error("質問は1000文字以内で入力してください");
  }
  return query.trim();
}
```