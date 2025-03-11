# PulseChain

PulseChainは従来のトリレンマ（分散化・スケーラビリティ・セキュリティ）を超えて、リアルタイム処理、環境融合、人間性を重視した、全く新しいレイヤーワンブロックチェーンです。

## 主な技術的特徴

1. **リアルタイムトランザクション処理（RTCS：Real-time Consensus Stream）**
   - ブロックチェーンの概念を廃止し、各トランザクションをリアルタイムに処理
   - ネットワークノードは即時に取引の正当性を検証・承認し、取引が即座に完了

2. **環境同期型コンセンサスメカニズム**
   - 環境データを元にしたVRF（Verifiable Random Function）によるリーダー選出
   - 公平性と安全性を確保した新しいコンセンサスアルゴリズム
   - 気象データ、経済指標、インターネットトラフィックなどの公開データを活用

3. **ゼロエネルギーノード運営**
   - 低消費電力設計によるエネルギー効率の最大化
   - 環境に優しい持続可能なブロックチェーンエコシステム
   - アダプティブコンピューティングによる動的なリソース調整

4. **人間的信頼形成システム（Human Trust Layer）**
   - ノードの信頼スコアによる協調的なネットワーク形成
   - 悪意のあるノードの排除をリアルタイムで実施
   - コミュニティ投票と行動履歴に基づく信頼性評価

5. **ダイナミックマイクロチェーン構造**
   - トランザクション負荷に応じて動的にスケールするネットワーク
   - 常に最適なパフォーマンスを維持
   - 一時的かつ動的にマイクロチェーンが生成・消滅

6. **ポスト量子暗号**
   - 量子コンピュータによる攻撃からネットワークを防御
   - CRYSTALS-Dilithiumなどの量子耐性暗号を採用
   - 長期的なセキュリティを確保

## プロジェクト構造

```
PulseChain/
├── pulsechain/             # コアライブラリ
│   ├── core/               # コア機能
│   │   ├── node.py                # ノードクラス
│   │   ├── transaction.py         # トランザクションクラス
│   │   ├── transaction_pool.py    # トランザクションプール
│   │   ├── trust_system.py        # 人間的信頼形成システム
│   │   └── microchain.py          # ダイナミックマイクロチェーン
│   ├── consensus/          # コンセンサスメカニズム
│   │   └── environmental.py       # 環境同期型コンセンサス
│   ├── network/            # ネットワーク通信
│   │   ├── api_server.py          # APIサーバー
│   │   └── browser_data_collector.py  # ブラウザデータ収集
│   ├── crypto/             # 暗号化機能
│   │   ├── signatures.py          # 署名機能
│   │   └── post_quantum.py        # ポスト量子暗号
│   └── utils/              # ユーティリティ
│       ├── vrf.py                 # 検証可能なランダム関数
│       ├── weather_api.py         # 気象API連携
│       ├── distributed_data_source.py  # 分散型データソース
│       └── energy_optimizer.py    # エネルギー最適化
├── web/                    # Webインターフェース
│   ├── src/                # Reactソースコード
│   │   ├── components/     # 共通コンポーネント
│   │   ├── pages/          # ページコンポーネント
│   │   └── ...
│   ├── public/             # 静的ファイル
│   └── ...
├── main.py                 # 基本的なノード実行スクリプト
├── enhanced_main.py        # 拡張機能付きノード実行スクリプト
├── zero_energy_main.py     # ゼロエネルギー最適化ノード実行スクリプト
└── advanced_pulsechain.py  # すべての機能を統合したノード実行スクリプト
```

## インストール方法

### バックエンド（Python）

```bash
# 必要なパッケージをインストール
pip install cryptography pycryptodome fastapi uvicorn asyncio psutil requests
```

### フロントエンド（React）

```bash
# webディレクトリに移動
cd web

# 依存関係をインストール
npm install

# 開発サーバーを起動
npm run dev
```

## 使用方法

### バックエンド

```bash
# 基本的なノードを起動
python main.py --port 52964

# ゼロエネルギーノードを起動
python zero_energy_main.py --port 52964 --target-cpu-usage 30.0

# 高度なノードを起動（すべての機能を有効化）
python advanced_pulsechain.py --port 52964
```

### フロントエンド

```bash
# webディレクトリに移動
cd web

# 開発サーバーを起動
npm run dev
```

## ライセンス

MIT