# Google Sheets統合AI面接システム 仕様書

## システム概要

### プロジェクト名
Radish AI面接システム (Google Sheets統合版)

### 目的
介護業界向けのAI面接官による自動面接システム。Google Sheetsを主要データソースとして使用し、質問管理、回答ログ、評価データの一元管理を実現。

### 開発期間
2025年6月27日 - 2025年7月1日

---

## システム構成

### アーキテクチャ
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   フロントエンド   │    │   バックエンド    │    │  Google Sheets  │
│   React/TS      │◄──►│  FastAPI/Python │◄──►│   データソース   │
│   Tailwind CSS  │    │   OpenAI API    │    │   ログ保存      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### 技術スタック

#### フロントエンド
- **フレームワーク**: React 18.2.0 + TypeScript
- **ビルドツール**: Vite 4.4.5
- **スタイリング**: Tailwind CSS 3.3.0
- **状態管理**: React Hooks (useState, useEffect)
- **HTTP通信**: Axios 1.5.1
- **音声機能**: Web Speech API
- **録画機能**: MediaRecorder API

#### バックエンド
- **フレームワーク**: FastAPI 0.104.1
- **言語**: Python 3.12
- **パッケージ管理**: Poetry
- **AI API**: OpenAI GPT-4
- **Google API**: Google Sheets API v4
- **認証**: Google Service Account
- **ログ管理**: CSV + Google Sheets

#### インフラ・デプロイ
- **フロントエンド**: Devin Apps Platform
- **バックエンド**: Fly.io
- **データストレージ**: Google Sheets
- **録画ファイル**: ローカルストレージ

---

## 公開URL

### 本番環境
- **フロントエンド**: https://radish-project-reader-gb4s8nsn.devinapps.com/
- **バックエンド**: https://app-jvyslirn.fly.dev/
- **Google Sheets**: https://docs.google.com/spreadsheets/d/1I0iovuV1lkwIC3lnx7gG92a2MRQu-hLYCdodBplxoNE/

### 開発環境
- **フロントエンド**: http://localhost:3000
- **バックエンド**: http://localhost:8000

---

## 機能仕様

### 1. 面接画面機能

#### 1.1 面接官表示
- **静止時**: PNG画像表示 (`/assets/interviewer.png`)
- **会話中**: MP4動画再生 (`/assets/interviewer.mp4`)
- **スタイル**: Zoom/Google Meet風のビデオ通話インターフェース
- **面接官**: 施設長不動 (ハードコード)

#### 1.2 コミュニケーション機能
- **テキスト入力**: リアルタイムメッセージ送信
- **音声認識**: Web Speech API使用
- **音声合成**: AI応答の音声読み上げ
- **AI応答**: OpenAI GPT-4による自然な対話

#### 1.3 録画機能
- **自動録画**: 面接開始時に自動開始
- **形式**: WebM形式
- **保存**: サーバーサイドストレージ
- **ダウンロード**: 管理画面からアクセス可能

### 2. Google Sheets統合機能

#### 2.1 データソース構造
```
Google Sheets (1I0iovuV1lkwIC3lnx7gG92a2MRQu-hLYCdodBplxoNE)
├── BasicQuestions      # 基本質問集
├── EvaluationCriteria  # 評価基準
├── NGWords            # NGワード集
├── InterviewFlow      # 面接フロー
├── OverallEvaluation  # 総合評価基準
└── logs              # Q&Aログ・評価データ
```

#### 2.2 質問管理
- **動的読み込み**: Google Sheetsから質問を動的取得
- **カテゴリ分類**: 自己紹介、職歴、志望動機、スキル等
- **段階的質問**: 対話回数に応じた適切な質問選択
- **フォローアップ**: 回答に基づく追加質問

#### 2.3 ログ機能
- **リアルタイム保存**: Q&A内容をlogsシートに即座保存
- **構造化データ**: 12メッセージ以上で自動的に構造化データ抽出
- **評価データ**: AI評価結果の自動保存
- **録画リンク**: 録画ファイルURLの保存

### 3. 管理画面機能

#### 3.1 面接記録管理
- **一覧表示**: 全面接記録の表形式表示
- **詳細表示**: 個別面接の詳細情報
- **検索・フィルタ**: 日付、名前による絞り込み
- **ソート機能**: 各列でのソート

#### 3.2 ファイル管理
- **録画ダウンロード**: 面接録画ファイルのダウンロード
- **CSVエクスポート**: 面接ログのCSV出力
- **データ分析**: 構造化された面接データの表示

---

## API仕様

### エンドポイント一覧

#### 1. 面接関連
```http
POST /api/chat/start
GET /api/interviewers
POST /api/chat/message
POST /api/upload_recording
```

#### 2. 管理関連
```http
GET /api/interview_records
GET /api/download_recording/{filename}
GET /api/download_csv
GET /api/extracted_data/{conversation_id}
GET /api/all_extracted_data
```

#### 3. ヘルスチェック
```http
GET /health
```

### 詳細仕様

#### POST /api/chat/start
面接セッション開始
```json
// Request
{
  "interviewer_id": "fudou"
}

// Response
{
  "conversation_id": "uuid",
  "greeting": "こんにちは...",
  "interviewer": {
    "id": "fudou",
    "name": "施設長不動",
    "image": "/assets/interviewer.png",
    "video": "/assets/interviewer.mp4"
  }
}
```

#### POST /api/chat/message
メッセージ送信・AI応答取得
```json
// Request
{
  "message": "ユーザーメッセージ",
  "conversation_id": "uuid",
  "interviewer_id": "fudou"
}

// Response
{
  "message": "AI応答メッセージ",
  "conversation_id": "uuid"
}
```

---

## データベース設計

### Google Sheets構造

#### BasicQuestions シート
| 列名 | 型 | 説明 |
|------|----|----|
| Category | String | 質問カテゴリ |
| Question | String | 質問内容 |
| Purpose | String | 質問目的 |
| Expected_Answer | String | 期待される回答 |
| Follow_Up | String | フォローアップ質問 |

#### logs シート
| 列名 | 型 | 説明 |
|------|----|----|
| Timestamp | DateTime | 記録日時 |
| Conversation_ID | String | 会話ID |
| Question | String | 質問内容 |
| Answer | String | 回答内容 |
| Evaluation | String | 評価コメント |
| Name | String | 応募者名 |
| Age | String | 年齢 |
| Experience | String | 経験 |
| Skills | String | スキル |
| Motivation | String | 志望動機 |
| Communication | String | コミュニケーション評価 |
| Learning_Attitude | String | 学習意欲評価 |
| Problem_Solving | String | 問題解決能力評価 |
| Completeness_Score | Number | 完全性スコア |
| Quality_Score | Number | 品質スコア |
| Recommendation | String | 推奨判定 |
| Recording_URL | String | 録画ファイルURL |

---

## セキュリティ仕様

### 認証・認可
- **Google Service Account**: elevated-nature-464503-k4@elevated-nature-464503-k4.iam.gserviceaccount.com
- **権限**: Google Sheets編集者権限
- **スコープ**: `https://www.googleapis.com/auth/spreadsheets`

### CORS設定
```python
origins = [
    "http://localhost:3000",
    "https://radish-project-reader-gb4s8nsn.devinapps.com",
    "https://*.devinapps.com",
    "https://app-jvyslirn.fly.dev"
]
```

### 環境変数
```bash
# OpenAI API
OPENAI_API_KEY=sk-...

# Google Sheets
GOOGLE_SERVICE_ACCOUNT_PATH=./google_service_account.json
SHEET_ID=1I0iovuV1lkwIC3lnx7gG92a2MRQu-hLYCdodBplxoNE

# サーバー設定
HOST=0.0.0.0
PORT=8000
```

---

## セットアップ手順

### 1. 環境準備
```bash
# リポジトリクローン
git clone https://github.com/Shimano02/Radish.git
cd Radish

# バックエンド
cd backend
poetry install
cp .env.example .env
# .envファイルを編集

# フロントエンド
cd ../frontend
npm install
```

### 2. Google Sheets設定
1. Google Cloud Consoleでサービスアカウント作成
2. 認証JSONファイルをダウンロード
3. Google Sheetsでサービスアカウントを編集者として追加
4. SHEET_IDを.envに設定

### 3. 起動
```bash
# バックエンド
cd backend
poetry run python main.py

# フロントエンド
cd frontend
npm run dev
```

---

## テスト仕様

### 単体テスト
- Google Sheets接続テスト
- 質問読み込みテスト
- Q&Aログ保存テスト
- API エンドポイントテスト

### 統合テスト
- 完全な面接フローテスト
- 録画機能テスト
- 管理画面機能テスト

### テストスクリプト
```bash
# Google Sheets統合テスト
poetry run python test_new_spreadsheet_integration.py

# 書き込み権限テスト
poetry run python test_write_permissions.py

# 完全面接フローテスト
poetry run python test_complete_interview_flow.py
```

---

## パフォーマンス仕様

### レスポンス時間
- **API応答**: < 3秒
- **AI応答生成**: < 10秒
- **Google Sheets読み込み**: < 2秒
- **ログ保存**: < 1秒

### 同時接続
- **想定ユーザー数**: 10-50名
- **セッション管理**: メモリベース
- **ファイルストレージ**: ローカルディスク

---

## 運用・保守

### ログ管理
- **アプリケーションログ**: Python logging
- **アクセスログ**: FastAPI自動生成
- **エラーログ**: 例外ハンドリング

### バックアップ
- **Google Sheets**: 自動バックアップ
- **録画ファイル**: 手動バックアップ推奨
- **設定ファイル**: Git管理

### 監視
- **ヘルスチェック**: `/health` エンドポイント
- **Google Sheets接続**: 定期チェック
- **ディスク容量**: 録画ファイル蓄積監視

---

## 既知の問題・制限事項

### 技術的制限
1. **CORS問題**: デプロイ環境でのCORS設定調整が必要
2. **セッション管理**: メモリベースのため再起動時にセッション消失
3. **ファイルストレージ**: ローカルストレージのため容量制限あり

### 機能制限
1. **同時面接数**: サーバーリソースに依存
2. **録画時間**: ブラウザ制限により長時間録画に制約
3. **音声認識**: ブラウザ対応状況に依存

---

## 今後の拡張予定

### 短期改善
- [ ] CORS問題の完全解決
- [ ] セッション永続化
- [ ] エラーハンドリング強化

### 中期改善
- [ ] データベース導入
- [ ] ユーザー認証機能
- [ ] 面接テンプレート機能

### 長期改善
- [ ] マルチテナント対応
- [ ] 高度な分析機能
- [ ] モバイルアプリ対応

---

## 連絡先・サポート

### 開発者
- **GitHub**: https://github.com/Shimano02/Radish
- **PR**: https://github.com/Shimano02/Radish/pull/1

### Devin実行ログ
- **セッションURL**: https://app.devin.ai/sessions/7d19ff3d28bb4eada81ed7a52c5f380d

---

## 更新履歴

| 日付 | バージョン | 変更内容 |
|------|-----------|----------|
| 2025-07-01 | 1.0.0 | Google Sheets統合版リリース |
| 2025-06-30 | 0.9.0 | CORS修正、デプロイ対応 |
| 2025-06-29 | 0.8.0 | Google Sheets統合実装 |
| 2025-06-28 | 0.7.0 | 面接官表示機能追加 |
| 2025-06-27 | 0.6.0 | 基本機能実装完了 |

---

*本仕様書は2025年7月1日時点の実装内容に基づいて作成されています。*
