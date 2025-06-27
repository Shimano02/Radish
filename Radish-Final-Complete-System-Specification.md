# Radish AI面接システム 最終仕様書

## システム概要

Radish AI面接システムは、AI面接官との対話形式面接を実現するWebアプリケーションです。求職者がブラウザ上でAI面接官「施設長不動」と面接を行い、音声・テキスト・ビデオ録画機能を通じて包括的な面接体験を提供します。

### 主要機能
- **直接チャット画面**: 面接官選択を廃止し、ハードコードされた面接官との直接対話
- **手動マイク制御**: ユーザーが任意でマイクのオン・オフを制御可能
- **リアルタイム音声認識**: 話している間のリアルタイム文字起こし表示
- **動的面接官表示**: Zoom/Meet風レイアウトでPNG/MP4切り替え
- **ビデオ録画**: 面接全体の録画・ダウンロード・サーバー保存
- **CSV日次ログ**: 会話内容の自動CSV保存（日次ローテーション）
- **YouTube風管理画面**: カード型レイアウトでの面接記録管理・ダウンロード

## 技術仕様

### アーキテクチャ
```
Frontend (React/TypeScript) ←→ Backend (Python/FastAPI) ←→ Dify AI API
```

### フロントエンド
- **フレームワーク**: React 18 + TypeScript + Vite
- **スタイリング**: Tailwind CSS
- **状態管理**: React Hooks (useState, useRef, useEffect)
- **音声機能**: Web Speech Recognition API (continuous mode)
- **録画機能**: MediaRecorder API (WebM形式)
- **UI**: Lucide React アイコン

### バックエンド
- **フレームワーク**: FastAPI + Python 3.12
- **依存管理**: Poetry
- **ログ管理**: CSV形式（日次ローテーション）
- **ファイル保存**: ローカルファイルシステム
- **AI連携**: Dify API

### 外部サービス
- **AI応答生成**: Dify AI Platform
- **音声合成**: ブラウザ内蔵 Speech Synthesis API

## 詳細機能仕様

### 1. 面接画面（ChatInterface）

#### 音声機能（手動制御）
- **連続録音**: `continuous = true` で手動停止まで録音継続
- **リアルタイム表示**: `interimResults = true` で話している間の文字表示
- **手動制御**: マイクボタンクリックでオン・オフ切り替え
- **エラーハンドリング**: マイク許可拒否時の適切な処理
- **自動再開**: 予期しない停止時の自動復旧機能

#### 面接官表示（Zoom/Meet風）
- **2画面レイアウト**: 面接官・面接者の並列表示
- **動的切り替え**: 
  - 静止時: PNG画像表示
  - AI応答中: MP4動画再生
- **円形アバター**: 128x128px 円形表示
- **状態表示**: 面接官名・タイトル表示

#### ビデオ録画
- **フォーマット**: WebM (ブラウザ標準)
- **制御**: 開始・一時停止・再開・停止
- **保存**: ローカルダウンロード + サーバーアップロード
- **プレビュー**: リアルタイム録画プレビュー

#### チャット機能
- **テキスト入力**: マルチライン対応
- **音声入力**: 手動制御マイク + リアルタイム表示
- **AI応答**: Dify API経由での自動応答
- **音声合成**: 日本語音声での応答読み上げ

### 2. 管理画面（AdminPanel）

#### YouTube風ダッシュボード
- **カードレイアウト**: 3列グリッド（レスポンシブ）
- **カード構成**:
  - 動画サムネイル（録画なしの場合はプレースホルダー）
  - 面接日時・面接官名・メッセージ数
  - 会話ID（短縮表示）
- **詳細モーダル**: カードクリックで詳細情報表示

#### ダウンロード機能
- **CSV**: 面接ログのCSVファイルダウンロード
- **動画**: 録画ファイルのダウンロード（実装済みの場合）
- **アクセス**: 詳細モーダル内のダウンロードボタン

### 3. データ管理

#### CSVログ形式
```csv
timestamp,conversation_id,role,message
2025-06-27 10:30:15,abc123,user,こんにちは
2025-06-27 10:30:20,abc123,assistant,こんにちは。面接を始めましょう。
```

#### ファイル構造
```
backend/
├── interview_logs/
│   ├── interview_log_2025-06-27.csv
│   └── interview_log_2025-06-28.csv
├── recordings/
│   ├── abc123.webm
│   └── def456.webm
└── main.py
```

## API仕様

### エンドポイント一覧

#### 1. チャット関連
```
POST /chat
- 面接メッセージ送信・AI応答取得
- Request: {message: string, conversation_id: string}
- Response: {response: string}
```

#### 2. 録画関連
```
POST /upload-recording
- 録画ファイルのサーバー保存
- Request: multipart/form-data (video file + conversation_id)
- Response: {message: string, filename: string}

GET /download-recording/{conversation_id}
- 録画ファイルのダウンロード
- Response: video/webm file
```

#### 3. ログ関連
```
GET /interview-records
- 面接記録一覧取得
- Response: [{conversation_id, timestamp, interviewer, message_count}]

GET /download-csv/{conversation_id}
- CSVログファイルのダウンロード
- Response: text/csv file
```

## セットアップ・運用

### 開発環境セットアップ
```bash
# バックエンド
cd backend
poetry install
poetry run uvicorn main:app --host 0.0.0.0 --port 8000 --reload

# フロントエンド
cd frontend
npm install
npm run dev
```

### 環境変数設定
```bash
# backend/.env
DIFY_API_KEY=your_dify_api_key
DIFY_API_URL=https://api.dify.ai/v1
```

### 本番環境要件
- **Node.js**: 18.x以上
- **Python**: 3.12以上
- **Poetry**: 最新版
- **ストレージ**: 録画ファイル用の十分な容量

## スケーラビリティ分析

### 現在の制約

#### 1日60件面接の技術的課題
1. **メモリ制約**:
   - セッションデータがメモリ内辞書で管理
   - 60分録画 × 60件 = 約180GB以上のメモリ必要
   - サーバー再起動でセッションデータ消失

2. **ストレージ制約**:
   - ローカルファイルシステムのみ
   - バックアップ・冗長化なし
   - 60分録画 × 60件 = 約360GB/日のストレージ必要

3. **同時実行制約**:
   - 単一サーバーでの処理限界
   - データベース未使用
   - 負荷分散機能なし

### 推奨改善策

#### フェーズ1: データベース導入（1-2ヶ月）
- PostgreSQL/MySQL導入
- セッション永続化
- 面接記録のDB管理
- **投資**: 開発2ヶ月 + DB月額$50-100

#### フェーズ2: クラウドストレージ（1ヶ月）
- AWS S3/Google Cloud Storage
- 録画ファイルのクラウド保存
- CDN配信最適化
- **投資**: 開発1ヶ月 + ストレージ月額$200-500

#### フェーズ3: 水平スケーリング（2-3ヶ月）
- Docker化・Kubernetes対応
- ロードバランサー導入
- Redis セッション管理
- **投資**: 開発3ヶ月 + インフラ月額$500-1000

#### フェーズ4: 高可用性（1-2ヶ月）
- マルチリージョン展開
- 自動バックアップ
- 監視・アラート機能
- **投資**: 開発2ヶ月 + 運用月額$300-600

### 総投資見積もり
- **開発期間**: 6-8ヶ月
- **初期投資**: $50,000-80,000（開発費）
- **月額運用**: $1,000-2,000（インフラ）

## 現在の実装状況

### ✅ 完了済み機能
- [x] 面接官選択画面削除
- [x] 直接チャット画面実装
- [x] CSV形式ログ保存（日次ローテーション）
- [x] YouTube風管理画面
- [x] 動画録画・ダウンロード機能
- [x] Zoom/Meet風面接官表示
- [x] 手動マイク制御（連続録音）
- [x] リアルタイム音声認識
- [x] CSVダウンロード機能

### ⚠️ 制限事項
- 1日60件の同時面接は技術的に不可能
- メモリ内セッション管理（永続化なし）
- ローカルストレージのみ（クラウド未対応）
- 単一サーバー構成（負荷分散なし）

### 🔄 推奨次期開発
1. データベース導入（PostgreSQL）
2. セッション永続化機能
3. クラウドストレージ連携
4. 負荷分散・水平スケーリング対応

## 技術的詳細

### 音声認識実装詳細
```typescript
// 連続録音設定
recognitionRef.current.continuous = true
recognitionRef.current.interimResults = true

// リアルタイム結果処理
recognitionRef.current.onresult = (event) => {
  let interimTranscript = ''
  let finalTranscript = ''
  
  for (let i = event.resultIndex; i < event.results.length; i++) {
    const transcript = event.results[i][0].transcript
    if (event.results[i].isFinal) {
      finalTranscript += transcript
    } else {
      interimTranscript += transcript
    }
  }
  
  if (finalTranscript) {
    setInputText(prev => prev + finalTranscript + ' ')
    setInterimText('')
  } else {
    setInterimText(interimTranscript)
  }
}

// 自動再開機能
recognitionRef.current.onend = () => {
  if (isVoiceRecording) {
    try {
      recognitionRef.current.start()
    } catch (error) {
      console.error('Failed to restart recognition:', error)
      setIsVoiceRecording(false)
    }
  }
}
```

### 面接官表示切り替え
```typescript
// 音声合成との連動
const utterance = new SpeechSynthesisUtterance(response.response)
utterance.onstart = () => setIsSpeaking(true)
utterance.onend = () => setIsSpeaking(false)

// 動的表示切り替え
{isSpeaking ? (
  <video src="/assets/interviewer-speaking.mp4" autoPlay loop muted />
) : (
  <img src="/assets/interviewer-static.png" alt="面接官" />
)}
```

## セキュリティ考慮事項

### データ保護
- 面接録画・ログの適切な保存期間設定
- 個人情報保護法対応
- GDPR対応（必要に応じて）

### アクセス制御
- 管理画面のアクセス制限
- API認証機能の追加検討
- ファイルダウンロードの権限管理

## 保守・運用

### 日常運用
- CSVログファイルの定期確認
- 録画ファイルの容量監視
- システムエラーログの確認

### 定期メンテナンス
- ログファイルのアーカイブ・削除
- 録画ファイルの整理
- システムアップデート

---

**作成日**: 2025年6月27日  
**バージョン**: v2.0  
**最終更新**: 手動マイク制御機能追加対応
