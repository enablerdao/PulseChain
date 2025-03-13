# PulseChain - 環境同期型ブロックチェーン

> **開発進捗状況**: 実装段階 | コア機能・ウェブインターフェース開発中 | 28 Pythonファイル | 最終更新: 2025年3月
> 
> PulseChainは実装段階にあり、コアブロックチェーン機能、環境同期型PoHコンセンサス、ハートビートプロトコルが実装されています。ウェブインターフェースとAPIサーバーも開発中です。

**このプロジェクトは[株式会社イネブラ](https://enablerhq.com)の実験的ブロックチェーンプロジェクトです。**

[English](README.en.md) | [中文](README.zh-CN.md) | [한국어](README.ko.md)

```
 ____        _          ____ _           _       
|  _ \ _   _| |___  ___/ ___| |__   __ _(_)_ __  
| |_) | | | | / __|/ _ \ |   | '_ \ / _` | | '_ \ 
|  __/| |_| | \__ \  __/ |___| | | | (_| | | | | |
|_|    \__,_|_|___/\___|\____|_| |_|\__,_|_|_| |_|
                                                  
```

PulseChainは、リアルタイム処理と環境データの活用を核とする次世代型ブロックチェーンプラットフォームです。SolanaのProof of History（PoH）メカニズムを基盤としながら、独自の「環境同期型コンセンサス」とP2Pネットワークにおける「ハートビート」メカニズムを組み合わせることで、ミリ秒単位の超高速合意形成を実現します。従来のブロックチェーンが抱える遅延問題を解消しつつ、高度な攻撃耐性とスケーラビリティを両立させる革新的な設計を提案します。

## 主な技術的特徴

```
┌───────────────────────────────────────────────────────────────┐
│                                                               │
│  ┌─────────────────────────┐      ┌─────────────────────────┐ │
│  │ 環境同期型PoH          │      │ ハートビートプロトコル   │ │
│  └─────────────────────────┘      └─────────────────────────┘ │
│                                                               │
│  ┌─────────────────────────┐      ┌─────────────────────────┐ │
│  │ リアルタイム処理        │      │ 階層型ネットワーク構造  │ │
│  └─────────────────────────┘      └─────────────────────────┘ │
│                                                               │
│  ┌─────────────────────────┐      ┌─────────────────────────┐ │
│  │ 高スループット処理      │      │ ポスト量子暗号         │ │
│  └─────────────────────────┘      └─────────────────────────┘ │
│                                                               │
└───────────────────────────────────────────────────────────────┘
```

## コア機能の詳細

### 1. 環境同期型PoH (Environmentally Synchronized Proof of History)

SolanaのPoHメカニズムを拡張し、外部環境データを統合したコンセンサスアルゴリズム：

- **PoHの基本メカニズム**:
  - 暗号学的に検証可能な時間の経過を証明するハッシュ連鎖
  - 連続的なハッシュ計算による時間証明
  - 数式: `next_hash = hash(previous_hash || counter || env_data_hash)`

- **環境データの統合**:
  - DEX取引データ、気象データ、市場フィードなどの外部データをハッシュ入力に含める
  - データの信頼性検証と重み付けによるコンセンサスの質向上
  - 環境データが「共通の外部参照点」として機能し、合意形成を加速

- **PoHリーダー選出**:
  - ステークベースの投票と過去のパフォーマンスに基づくリーダー選出
  - リージョンごとに別々のリーダーを選出し、地理的冗長性を確保
  - リーダー間の連携によるグローバルPoHタイムラインの統合

- **検証プロセス**:
  - PoHリーダーがタイムラインを生成し、環境データを統合
  - 検証ノードがPoHチェーンの整合性を検証
  - 過半数の検証ノード同意によるタイムライン確定

### 2. ハートビートプロトコル

PoH上に構築されたリアルタイム検証システム：

- **ハートビートの構造**:
  - PoHスロット参照、対応するPoHハッシュ、ノード識別子を含む
  - ノード固有シーケンス番号によるリプレイ攻撃防止
  - Ed25519署名による認証
  - 数式: `heartbeat = {poh_slot, poh_hash, node_id, sequence, timestamp, signature}`

- **ハートビートの役割**:
  - ノード状態のリアルタイム監視
  - PoHタイムラインとの時間同期確認
  - ネットワーク遅延やビザンチン挙動の検出
  - トランザクション検証の効率化

- **ハートビート伝播メカニズム**:
  - 階層型伝播による効率的な通信
  - ネットワーク負荷に応じた動的周波数調整（0.05-0.5秒）
  - 重要性に基づく優先度付け

- **PoHとハートビートの連携**:
  - PoHチェーンの各ポイントで複数ノードのハートビートを収集
  - ハートビートのクラスタリングによる時間同期の検証
  - 異常値の検出と除外による堅牢性確保

### 3. リアルタイム処理

ミリ秒単位の超高速トランザクション処理：

- **ブロックレス設計**:
  - 従来のブロック構造を廃止し、各トランザクションを独立して処理
  - トランザクションストリームの連続的な検証と承認
  - 数式: `ConfirmationTime = NetworkLatency + ValidationTime + ConsensusTime`

- **並列処理アーキテクチャ**:
  - 依存関係のないトランザクションの同時処理
  - マルチコア最適化による高スループット
  - 数式: `SystemThroughput = Σ(NodeCapacity_i * ParticipationFactor_i)`

- **即時ファイナリティ**:
  - 単一ラウンドでのトランザクション確定
  - 確率的ファイナリティではなく確定的ファイナリティを実現
  - 平均確認時間: 100-500ミリ秒

### 4. 階層型ネットワーク構造

地理的リージョンごとのサブネットワークによる効率化：

- **システム全体構成**:
  - コアPoHネットワークを中心とした階層構造
  - 地理的リージョンごとのサブネットワーク
  - 環境データプロバイダーとの連携

- **リージョン間連携**:
  - クロスリージョン通信の最適化
  - リージョン間の冗長経路によるネットワーク分断耐性
  - グローバルな状態同期メカニズム

- **スケーラビリティ設計**:
  - リージョンベースのシャーディング
  - PoHリーダー間の階層構造によるスケーラビリティ
  - トランザクション処理の並列化

### 5. ポスト量子暗号

量子コンピュータに耐える暗号技術：

- **格子ベース暗号**:
  - CRYSTALS-Dilithiumによるデジタル署名
  - CRYSTALS-Kyberによる鍵交換
  - 理論的に量子アルゴリズムに対する耐性を持つ設計

- **ハイブリッド暗号アプローチ**:
  - 従来の楕円曲線暗号とポスト量子暗号の併用
  - 段階的な移行戦略
  - 両方の暗号システムの長所を活かした設計

- **セキュリティ対策**:
  - Ed25519署名によるPoHチェーンの保護
  - 環境データの多重検証によるタイムライン操作の防止
  - ステークベースの参加資格確認によるSybil攻撃対策

## プロジェクト構造

```
PulseChain/
├── pulsechain/             # コアライブラリ
│   ├── core/               # コア機能
│   │   ├── node.py                # ノードクラス
│   │   ├── transaction.py         # トランザクションクラス
│   │   ├── transaction_pool.py    # トランザクションプール
│   │   ├── poh_generator.py       # PoH生成エンジン
│   │   └── region_manager.py      # リージョン管理
│   ├── consensus/          # コンセンサスメカニズム
│   │   ├── poh.py                 # Proof of History実装
│   │   └── env_sync.py            # 環境同期型コンセンサス
│   ├── network/            # ネットワーク通信
│   │   ├── heartbeat.py           # ハートビートプロトコル
│   │   ├── api_server.py          # APIサーバー
│   │   └── region_sync.py         # リージョン間同期
│   ├── crypto/             # 暗号化機能
│   │   ├── signatures.py          # Ed25519署名
│   │   └── post_quantum.py        # ポスト量子暗号
│   └── utils/              # ユーティリティ
│       ├── env_data_collector.py  # 環境データ収集
│       ├── market_api.py          # 市場データAPI連携
│       ├── weather_api.py         # 気象API連携
│       └── time_sync.py           # 時間同期ユーティリティ
├── web/                    # Webインターフェース
│   ├── src/                # Reactソースコード
│   │   ├── components/     # 共通コンポーネント
│   │   ├── pages/          # ページコンポーネント
│   │   └── ...
│   ├── public/             # 静的ファイル
│   └── ...
├── main.py                 # 基本的なノード実行スクリプト
├── poh_leader.py           # PoHリーダーノード実行スクリプト
├── validator_node.py       # 検証ノード実行スクリプト
└── advanced_pulsechain.py  # すべての機能を統合したノード実行スクリプト
```

## インストール方法

### バックエンド（Python）

```bash
# 必要なパッケージをインストール
pip install cryptography pycryptodome fastapi uvicorn asyncio psutil requests ed25519 numpy
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
python main.py --port 52964 --region asia

# PoHリーダーノードを起動
python poh_leader.py --port 52964 --region asia --env-data-sources market,weather

# 検証ノードを起動
python validator_node.py --port 52965 --leader-address 127.0.0.1:52964 --heartbeat-interval 0.1

# Solana軽量ノードを起動（Solanaデータを環境データとして統合）
python solana_light_node.py --port 52966 --region asia --solana-cluster mainnet-beta --leader-address 127.0.0.1:52964

# 高度なノードを起動（すべての機能を有効化）
python advanced_pulsechain.py --port 52964 --region asia --enable-all
```

### 環境データソースの設定

```bash
# 環境データソース設定ファイルを作成
cat > env_sources.json << EOF
{
  "market": {
    "api_url": "https://api.example.com/market",
    "update_interval": 5,
    "weight": 0.4
  },
  "weather": {
    "api_url": "https://api.example.com/weather",
    "update_interval": 60,
    "weight": 0.3
  },
  "time": {
    "ntp_servers": ["pool.ntp.org", "time.google.com"],
    "update_interval": 10,
    "weight": 0.3
  }
}
EOF

# 環境データソース設定を指定してノードを起動
python poh_leader.py --port 52964 --env-config env_sources.json
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

## 実装ロードマップ

```
┌────────────────────┐     ┌────────────────────┐     ┌────────────────────┐     ┌────────────────────┐
│ フェーズ1: 基盤開発 │ ──> │ フェーズ2: アルファ  │ ──> │ フェーズ3: ベータ   │ ──> │ フェーズ4: メインネット │
│ 2025年Q1-Q2        │     │ 2025年Q3           │     │ 2025年Q4-2026年Q1  │     │ 2026年Q2-Q3        │
└────────────────────┘     └────────────────────┘     └────────────────────┘     └────────────────────┘
```

### フェーズ1: 基盤開発 (6ヶ月)

- PoHエンジンの実装とカスタマイズ
- ハートビートプロトコルの設計と実装
- 環境データ統合インターフェースの開発
- 小規模テストネット (10-20ノード) の構築

### フェーズ2: アルファネットワーク (4ヶ月)

- 単一リージョンでの完全機能テスト
- ステーク管理システムの実装
- 基本的なスマートコントラクト機能の実装
- 初期開発者ツールの提供

### フェーズ3: ベータネットワーク (6ヶ月)

- マルチリージョン展開 (3-5リージョン)
- クロスリージョン通信の最適化
- スマートコントラクトのフル実装
- 100ノード規模のスケーラビリティテスト

### フェーズ4: メインネット (6ヶ月)

- セキュリティ監査と脆弱性対策
- パフォーマンスチューニング
- 完全なエコシステム開発ツールの提供
- メインネットローンチ

## ユースケースと応用

### 金融アプリケーション

- **超高速DEX**: ミリ秒レベルの注文処理による裁定取引の最小化
- **リアルタイム取引**: 中央取引所に匹敵する速度での取引処理
- **マイクロペイメント**: 小額決済の効率的処理

### IoTアプリケーション

- **センサーデータ検証**: 産業用IoTセンサーからのデータをリアルタイムで検証
- **自律システム間通信**: 自動運転車両間の安全な通信基盤
- **サプライチェーン管理**: 物流データのリアルタイム追跡と検証

### ゲームとメタバース

- **リアルタイムインゲーム取引**: ゲーム内アイテムやリソースの即時取引
- **メタバース間接続**: 異なる仮想世界間のアセット移動
- **ゲーム内経済の構築**: マイクロトランザクションに最適化された経済圏

## コミュニティと貢献

- **Discord**: [PulseChain Community](https://discord.gg/pulsechain)
- **Twitter**: [@PulseChain](https://twitter.com/PulseChain)
- **開発者ドキュメント**: [docs.pulsechain.org](https://docs.pulsechain.org)

## 関連プロジェクト

株式会社イネブラが開発する他のブロックチェーンプロジェクトもご覧ください：

- [NovaLedger](https://github.com/enablerdao/NovaLedger) - 超高速処理、高スケーラビリティ、量子耐性、AIによる最適化を特徴とする次世代ブロックチェーン技術
- [NexaCore](https://github.com/enablerdao/NexaCore) - AI統合、シャーディング、zk-SNARKsを特徴とする次世代ブロックチェーンプラットフォーム
- [OptimaChain](https://github.com/enablerdao/OptimaChain) - 革新的なスケーリング技術と高度なセキュリティを統合した分散型ブロックチェーンプラットフォーム
- [NeuraChain](https://github.com/enablerdao/NeuraChain) - AI、量子耐性、スケーラビリティ、完全な分散化、エネルギー効率を統合した次世代ブロックチェーン

## 参考文献

1. "Solana: A new architecture for a high performance blockchain" - Anatoly Yakovenko
2. "Proof of History: A clock for blockchain" - Solana Labs
3. "IoT Adaptive Dynamic Blockchain Networking Method Based on Discrete Heartbeat Signals" - IEEE
4. "Practical Byzantine Fault Tolerance" - Miguel Castro, Barbara Liskov
5. "TrueTime: Building a Distributed System with Synchronized Clocks" - Google
6. "Ed25519: High-speed high-security signatures" - Daniel J. Bernstein et al.