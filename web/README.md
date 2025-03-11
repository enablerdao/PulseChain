# PulseChain 環境同期型コンセンサス ウェブサイト

PulseChainの環境同期型コンセンサスメカニズムを説明するウェブサイトです。環境データの収集から検証プロセスまで、PulseChainの革新的な技術を詳しく解説しています。

## 機能

- **ホームページ**: PulseChainの概要と環境同期型コンセンサスの基本的な流れを紹介
- **データ収集ページ**: 多様なデータソースからの環境データ収集方法を詳細に説明
- **検証プロセスページ**: 収集したデータの検証方法とセキュリティ・信頼性の確保方法を解説
- **ライブデモページ**: 環境データの収集からリーダー選出までの流れをインタラクティブに体験できるシミュレーション

## 技術スタック

- **フロントエンド**: React, TypeScript, Vite
- **UI**: Material-UI (MUI)
- **グラフ**: Chart.js, react-chartjs-2
- **コード表示**: react-syntax-highlighter
- **ルーティング**: React Router

## インストール方法

```bash
# リポジトリのクローン
git clone https://github.com/yourusername/pulsechain-web.git
cd pulsechain-web

# 依存関係のインストール
npm install

# 開発サーバーの起動
npm run dev
```

## ビルド方法

```bash
# 本番用ビルド
npm run build

# ビルド結果のプレビュー
npm run preview
```

## プロジェクト構造

```
pulsechain-web/
├── src/
│   ├── components/       # 共通コンポーネント
│   │   ├── CodeBlock.tsx        # コードブロック表示
│   │   ├── DataFlowDiagram.tsx  # データフロー図
│   │   ├── DataSourceCard.tsx   # データソースカード
│   │   ├── Footer.tsx           # フッター
│   │   └── Header.tsx           # ヘッダー
│   ├── pages/           # ページコンポーネント
│   │   ├── Home.tsx             # ホームページ
│   │   ├── DataCollection.tsx   # データ収集ページ
│   │   ├── VerificationProcess.tsx  # 検証プロセスページ
│   │   └── LiveDemo.tsx         # ライブデモページ
│   ├── assets/          # 静的アセット
│   ├── App.tsx          # メインアプリケーション
│   └── main.tsx         # エントリーポイント
├── public/              # 公開ファイル
└── index.html           # HTMLテンプレート
```

## ライセンス

MIT

## 作者

OpenHands
