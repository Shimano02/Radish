# Radish AI面接システム

AI技術を活用した自動面接システムです。求職者がAI面接官と対話形式で面接を行い、面接記録を効率的に管理できます。

## 🚀 主要機能

- **直接チャット画面アクセス** - 面接官選択を省略し、すぐに面接開始
- **AI対話機能** - テキスト入力・音声認識による自然な対話
- **ビデオ録画** - 面接の様子を録画・保存
- **CSV形式ログ** - 面接内容を構造化データで保存
- **管理画面** - 面接記録の一覧表示・管理

## 🛠 技術スタック

### フロントエンド
- React 18.3.1 + TypeScript
- Vite (ビルドツール)
- Tailwind CSS (スタイリング)
- Lucide React (アイコン)

### バックエンド
- Python 3.12+ + FastAPI
- Poetry (依存関係管理)
- Dify API (AI応答生成)

## 📋 前提条件

- Node.js 18以上
- Python 3.12以上
- Poetry
- Dify APIキー

## 🔧 セットアップ手順

### 1. リポジトリのクローン
```bash
git clone https://github.com/Shimano02/Radish.git
cd Radish
```

### 2. バックエンドのセットアップ
```bash
cd backend
poetry install
cp .env.example .env
# .envファイルにDify APIキーを設定
poetry run python main.py
```

### 3. フロントエンドのセットアップ
```bash
cd frontend
npm install
npm run dev
```

## ⚙️ 環境変数設定

### backend/.env
```env
DIFY_API_KEY=your_dify_api_key_here
DIFY_BASE_URL=https://api.dify.ai/v1
```

### frontend/.env
```env
VITE_API_BASE_URL=http://localhost:8000
```

## 🖥 使用方法

### 面接の実施
1. アプリケーション起動後、自動的にチャット画面が表示されます
2. テキスト入力またはマイクボタンで音声入力が可能です
3. ビデオ録画ボタンで面接の様子を録画できます
4. 面接内容は自動的にCSVファイルに保存されます

### 管理画面の使用
1. チャット画面右上の「管理画面」ボタンをクリック
2. 面接記録の一覧が表示されます
3. 録画ファイルのダウンロードが可能です

## 📁 プロジェクト構造

```
Radish/
├── frontend/                 # React フロントエンド
│   ├── src/
│   │   ├── components/      # UIコンポーネント
│   │   ├── hooks/          # カスタムフック
│   │   ├── services/       # API クライアント
│   │   └── types.ts        # 型定義
│   └── package.json
├── backend/                 # FastAPI バックエンド
│   ├── main.py             # メインアプリケーション
│   ├── interview_logs/     # CSV ログファイル
│   ├── video_recordings/   # 録画ファイル
│   └── pyproject.toml
└── README.md
```

## 🔌 API エンドポイント

### 面接関連
- `POST /api/chat/start` - 面接セッション開始
- `POST /api/chat/message` - メッセージ送信・AI応答取得

### 管理関連
- `GET /api/admin/records` - 面接記録一覧取得
- `POST /api/admin/upload-recording` - 録画ファイルアップロード
- `GET /api/admin/recording/{record_id}` - 録画ファイルダウンロード

## 📊 データ形式

### CSV ログ形式
```csv
タイムスタンプ,会話ID,面接官ID,面接官名,ユーザーメッセージ,AI応答,対話回数,ステージ
```

## 🐛 既知の問題

- **手動ボタンクリック問題**: UIでの手動ボタンクリックが動作しない場合があります
  - 回避策: ブラウザの開発者ツールからプログラム的にクリック可能

## 🔍 トラブルシューティング

### よくある問題

1. **Dify API接続エラー**
   - `.env`ファイルのAPIキーを確認してください
   - Dify APIの利用制限を確認してください

2. **音声認識が動作しない**
   - ブラウザのマイク許可を確認してください
   - HTTPS環境での実行を推奨します

3. **ビデオ録画ができない**
   - ブラウザのカメラ・画面共有許可を確認してください

## 📝 開発・運用

### 開発モード
```bash
# バックエンド
cd backend && poetry run python main.py

# フロントエンド
cd frontend && npm run dev
```

### ログ管理
- CSV ログは日次で自動分割されます
- ファイル場所: `backend/interview_logs/`

### ビデオファイル管理
- 録画ファイル場所: `backend/video_recordings/`
- 定期的なディスク容量監視を推奨します

## 🤝 貢献

1. このリポジトリをフォーク
2. 機能ブランチを作成 (`git checkout -b feature/amazing-feature`)
3. 変更をコミット (`git commit -m 'Add amazing feature'`)
4. ブランチにプッシュ (`git push origin feature/amazing-feature`)
5. プルリクエストを作成

## 📄 ライセンス

このプロジェクトは MIT ライセンスの下で公開されています。

## 📞 サポート

問題や質問がある場合は、GitHubのIssuesページでお知らせください。

---

**作成者**: 島野将 (@Shimano02)  
**最終更新**: 2025年6月27日
