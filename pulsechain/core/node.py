"""
PulseChainノードの実装
"""

import time
import threading
import logging
import random
from typing import Dict, List, Optional, Set, Callable, Any
from .transaction import Transaction
from .transaction_pool import TransactionPool
from .trust_system import TrustSystem
from .microchain import MicroChainManager, MicroChain
from ..consensus.environmental import EnvironmentalConsensus, EnvironmentalData
from ..crypto.signatures import generate_key_pair, derive_address_from_public_key
from ..crypto.post_quantum import PostQuantumCrypto


# ロガーの設定
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("PulseChainNode")


class Node:
    """PulseChainノード - ネットワークの基本単位"""
    
    def __init__(self, node_id: Optional[str] = None, use_quantum_crypto: bool = True):
        """
        ノードの初期化
        
        Args:
            node_id: ノードの識別子（指定がなければ自動生成）
            use_quantum_crypto: 量子耐性暗号を使用するかどうか
        """
        # 暗号化機能の初期化
        self.quantum_crypto = PostQuantumCrypto()
        
        # 鍵ペアの生成（通常の鍵ペアと量子耐性鍵ペア）
        self.private_key, self.public_key = generate_key_pair()
        self.quantum_private_key, self.quantum_public_key = self.quantum_crypto.generate_keypair() if use_quantum_crypto else (None, None)
        
        # ノードIDの設定
        self.node_id = node_id or derive_address_from_public_key(self.public_key)
        
        # アドレスの導出
        self.address = derive_address_from_public_key(self.public_key)
        self.quantum_address = self.quantum_crypto.derive_address(self.quantum_public_key) if use_quantum_crypto else None
        
        # トランザクションプールの初期化
        self.tx_pool = TransactionPool()
        
        # コンセンサスメカニズムの初期化
        self.consensus = EnvironmentalConsensus(self.node_id, self.private_key)
        
        # 処理済みトランザクションのキャッシュ
        self.processed_tx_cache: Set[str] = set()
        
        # ノードの状態
        self.is_running = False
        self.is_leader = False
        
        # 処理スレッド
        self.consensus_thread = None
        self.processing_thread = None
        self.microchain_thread = None
        
        # ピア管理
        self.peers: Dict[str, Any] = {}  # ノードID -> ピア情報
        
        # 処理済みトランザクションのコールバック
        self.tx_processed_callbacks: List[Callable[[Transaction], None]] = []
        
        # エネルギー効率のための設定
        self.throttle_rate = 0.0  # スロットリング率（0.0〜1.0）
        self.adaptive_interval = 0.1  # 適応的な処理間隔（秒）
        self.energy_saving_mode = False  # 省エネモード
        self.battery_level = 100.0  # バッテリーレベル（%）
        
        # 信頼システムの初期化
        self.trust_system = TrustSystem()
        
        # マイクロチェーンマネージャーの初期化
        self.microchain_manager = MicroChainManager()
        
        # 現在参加しているマイクロチェーン
        self.active_microchains: Dict[str, MicroChain] = {}
        
        # 使用中の暗号化方式
        self.use_quantum_crypto = use_quantum_crypto
        
        logger.info(f"Node initialized with ID: {self.node_id}")
        if use_quantum_crypto:
            logger.info(f"Quantum-resistant cryptography enabled: {self.quantum_crypto.get_algorithm_info()['name']}")
            logger.info(f"Quantum address: {self.quantum_address}")
    
    def start(self) -> None:
        """ノードを起動"""
        if self.is_running:
            return
        
        self.is_running = True
        
        # マイクロチェーンマネージャーの起動
        self.microchain_manager.start()
        
        # コンセンサススレッドの開始
        self.consensus_thread = threading.Thread(target=self._consensus_loop)
        self.consensus_thread.daemon = True
        self.consensus_thread.start()
        
        # 処理スレッドの開始
        self.processing_thread = threading.Thread(target=self._processing_loop)
        self.processing_thread.daemon = True
        self.processing_thread.start()
        
        # マイクロチェーン管理スレッドの開始
        self.microchain_thread = threading.Thread(target=self._microchain_loop)
        self.microchain_thread.daemon = True
        self.microchain_thread.start()
        
        # 信頼システムにオンライン状態を記録
        self.trust_system.record_online_status(self.node_id, True)
        
        logger.info(f"Node {self.node_id} started")
    
    def stop(self) -> None:
        """ノードを停止"""
        self.is_running = False
        
        # 信頼システムにオフライン状態を記録
        self.trust_system.record_online_status(self.node_id, False)
        
        # マイクロチェーンマネージャーの停止
        self.microchain_manager.stop()
        
        # アクティブなマイクロチェーンから離脱
        for chain_id in list(self.active_microchains.keys()):
            self._leave_microchain(chain_id)
        
        # スレッドの終了を待機
        if self.consensus_thread:
            self.consensus_thread.join(timeout=2.0)
        
        if self.processing_thread:
            self.processing_thread.join(timeout=2.0)
        
        if self.microchain_thread:
            self.microchain_thread.join(timeout=2.0)
        
        logger.info(f"Node {self.node_id} stopped")
    
    def add_transaction(self, tx: Transaction) -> bool:
        """
        トランザクションを追加
        
        Args:
            tx: 追加するトランザクション
            
        Returns:
            bool: 追加に成功した場合はTrue、そうでない場合はFalse
        """
        # 既に処理済みのトランザクションは無視
        if tx.hash in self.processed_tx_cache:
            return False
        
        # トランザクションプールに追加
        return self.tx_pool.add_transaction(tx)
    
    def create_transaction(self, recipient: str, amount: float, 
                           data: Optional[Dict[str, Any]] = None) -> Transaction:
        """
        新しいトランザクションを作成
        
        Args:
            recipient: 受信者のアドレス
            amount: 送金額
            data: 追加データ
            
        Returns:
            Transaction: 作成されたトランザクション
        """
        # トランザクションの作成
        tx = Transaction(
            sender=self.address,
            recipient=recipient,
            amount=amount,
            data=data
        )
        
        # トランザクションに署名
        tx.sign(self.private_key)
        
        # トランザクションプールに追加
        self.add_transaction(tx)
        
        return tx
    
    def add_environmental_data(self, data: EnvironmentalData) -> None:
        """
        環境データを追加
        
        Args:
            data: 追加する環境データ
        """
        self.consensus.add_environmental_data(data)
        
        # バッテリーレベルの更新（温度をバッテリーレベルとして使用）
        if data.source_id.startswith("browser-"):
            self.battery_level = data.temperature
            
            # バッテリーレベルが低い場合は省エネモードを有効化
            if self.battery_level < 20.0 and not self.energy_saving_mode:
                self.energy_saving_mode = True
                logger.info(f"Battery level low ({self.battery_level:.1f}%), enabling energy saving mode")
            elif self.battery_level >= 30.0 and self.energy_saving_mode:
                self.energy_saving_mode = False
                logger.info(f"Battery level restored ({self.battery_level:.1f}%), disabling energy saving mode")
    
    def register_tx_processed_callback(self, callback: Callable[[Transaction], None]) -> None:
        """
        トランザクション処理時のコールバックを登録
        
        Args:
            callback: トランザクション処理時に呼び出される関数
        """
        self.tx_processed_callbacks.append(callback)
    
    def set_throttle_rate(self, rate: float) -> None:
        """
        スロットリング率を設定
        
        Args:
            rate: スロットリング率（0.0〜1.0）
        """
        self.throttle_rate = max(0.0, min(rate, 0.9))
        
        # 適応的な処理間隔を更新
        # スロットリング率が高いほど、処理間隔が長くなる
        self.adaptive_interval = 0.1 + self.throttle_rate * 0.9
        
        if self.throttle_rate > 0.5:
            logger.debug(f"High throttle rate ({self.throttle_rate:.2f}), adaptive interval: {self.adaptive_interval:.2f}s")
    
    def _consensus_loop(self) -> None:
        """コンセンサスループ - 定期的にコンセンサスを実行"""
        while self.is_running:
            try:
                # 省エネモードの場合、コンセンサス実行の確率を下げる
                if self.energy_saving_mode and random.random() < 0.7:
                    time.sleep(self.adaptive_interval * 2)
                    continue
                
                # ピア数の取得（実際のネットワークでは動的に変化）
                peer_count = max(1, len(self.peers) + 1)  # 自分自身を含む
                
                # コンセンサスの実行
                is_leader, random_value, proof = self.consensus.run_consensus(peer_count)
                
                if is_leader != self.is_leader:
                    self.is_leader = is_leader
                    if is_leader:
                        logger.info(f"Node {self.node_id} became leader")
                    else:
                        logger.info(f"Node {self.node_id} is no longer leader")
                
                # 適応的な間隔でスリープ
                sleep_time = self.adaptive_interval
                if self.energy_saving_mode:
                    # 省エネモードではさらに間隔を長くする
                    sleep_time *= 2
                
                time.sleep(sleep_time)
                
            except Exception as e:
                logger.error(f"Error in consensus loop: {e}")
                time.sleep(1.0)
    
    def _processing_loop(self) -> None:
        """処理ループ - トランザクションを処理"""
        while self.is_running:
            try:
                # リーダーの場合のみトランザクションを処理
                if self.is_leader:
                    # 省エネモードの場合、処理するトランザクション数を減らす
                    max_tx = 10
                    if self.energy_saving_mode:
                        max_tx = 3
                    
                    # スロットリング率に基づいて処理を間引く
                    if random.random() >= self.throttle_rate:
                        # トランザクションの処理
                        processed = self.tx_pool.process_transactions(
                            processor=self._process_transaction,
                            max_count=max_tx
                        )
                        
                        if processed:
                            logger.info(f"Processed {len(processed)} transactions")
                
                # 適応的な間隔でスリープ
                sleep_time = self.adaptive_interval
                if self.energy_saving_mode:
                    # 省エネモードではさらに間隔を長くする
                    sleep_time *= 2
                
                time.sleep(sleep_time)
                
            except Exception as e:
                logger.error(f"Error in processing loop: {e}")
                time.sleep(1.0)
    
    def _process_transaction(self, tx: Transaction) -> bool:
        """
        トランザクションを処理
        
        Args:
            tx: 処理するトランザクション
            
        Returns:
            bool: 処理に成功した場合はTrue、そうでない場合はFalse
        """
        # トランザクションの検証
        is_valid = False
        
        # 通常の署名検証
        if tx.verify():
            is_valid = True
        # 量子耐性署名の検証（実装されている場合）
        elif hasattr(tx, 'quantum_verify') and tx.quantum_verify():
            is_valid = True
        
        if not is_valid:
            logger.warning(f"Transaction verification failed: {tx.hash}")
            # 信頼システムに無効なトランザクションを記録
            self.trust_system.record_transaction(tx.sender, False)
            return False
        
        # 送信者がブラックリストに登録されていないか確認
        if self.trust_system.is_blacklisted(tx.sender):
            logger.warning(f"Transaction from blacklisted node rejected: {tx.hash}")
            return False
        
        # 実際のアプリケーションでは、ここでトランザクションの内容に基づいて
        # 状態の更新やスマートコントラクトの実行などを行います
        
        # 省エネモードの場合、処理を簡略化
        if not self.energy_saving_mode:
            # 通常モードでは追加の検証や処理を行う
            # （実際のアプリケーションではここに追加の処理を実装）
            pass
        
        # 処理済みキャッシュに追加
        self.processed_tx_cache.add(tx.hash)
        
        # キャッシュサイズの制限（最大10000件、省エネモードでは5000件）
        max_cache = 10000
        if self.energy_saving_mode:
            max_cache = 5000
            
        if len(self.processed_tx_cache) > max_cache:
            # 古いものから削除（実際の実装ではより洗練された方法が必要）
            self.processed_tx_cache = set(list(self.processed_tx_cache)[-max_cache:])
        
        # 信頼システムに有効なトランザクションを記録
        self.trust_system.record_transaction(tx.sender, True)
        
        # コールバックの呼び出し
        for callback in self.tx_processed_callbacks:
            try:
                callback(tx)
            except Exception as e:
                logger.error(f"Error in transaction callback: {e}")
        
        return True
    
    def _microchain_loop(self) -> None:
        """マイクロチェーン管理ループ - マイクロチェーンの作成・参加・離脱を管理"""
        while self.is_running:
            try:
                # 負荷に応じてマイクロチェーンを動的に管理
                self._manage_microchains()
                
                # 適応的な間隔でスリープ
                sleep_time = self.adaptive_interval * 5  # マイクロチェーン管理は頻繁に行う必要はない
                if self.energy_saving_mode:
                    sleep_time *= 2
                
                time.sleep(sleep_time)
                
            except Exception as e:
                logger.error(f"Error in microchain loop: {e}")
                time.sleep(1.0)
    
    def _manage_microchains(self) -> None:
        """負荷に応じてマイクロチェーンを動的に管理"""
        # トランザクションプールのサイズを取得
        pool_size = self.tx_pool.size()
        
        # 負荷が高い場合は新しいマイクロチェーンを作成
        if pool_size > 100 and len(self.active_microchains) < 5:
            self._create_microchain("high_load")
        
        # 負荷が低い場合は不要なマイクロチェーンから離脱
        elif pool_size < 10 and len(self.active_microchains) > 1:
            # 最も古いマイクロチェーンから離脱
            oldest_chain_id = min(
                self.active_microchains.keys(),
                key=lambda chain_id: self.active_microchains[chain_id].creation_time
            )
            self._leave_microchain(oldest_chain_id)
        
        # 信頼性の高いノードが作成したマイクロチェーンに参加
        trusted_nodes = self.trust_system.get_trusted_nodes(min_reliability=0.8)
        for node_id in trusted_nodes:
            if node_id in self.peers and 'microchains' in self.peers[node_id]:
                for chain_id in self.peers[node_id]['microchains']:
                    if chain_id not in self.active_microchains and len(self.active_microchains) < 5:
                        self._join_microchain(chain_id)
    
    def _create_microchain(self, purpose: str) -> Optional[str]:
        """
        新しいマイクロチェーンを作成
        
        Args:
            purpose: チェーンの目的
            
        Returns:
            Optional[str]: 作成されたマイクロチェーンのID、失敗した場合はNone
        """
        try:
            # 省エネモードの場合はマイクロチェーンを作成しない
            if self.energy_saving_mode:
                return None
            
            # マイクロチェーンを作成
            chain = self.microchain_manager.create_chain(purpose=purpose)
            
            # 参加ノードとして自分自身を追加
            chain.add_participating_node(self.node_id)
            
            # アクティブなマイクロチェーンに追加
            self.active_microchains[chain.chain_id] = chain
            
            logger.info(f"Created new microchain: {chain.chain_id} for purpose: {purpose}")
            
            return chain.chain_id
            
        except Exception as e:
            logger.error(f"Error creating microchain: {e}")
            return None
    
    def _join_microchain(self, chain_id: str) -> bool:
        """
        既存のマイクロチェーンに参加
        
        Args:
            chain_id: 参加するマイクロチェーンのID
            
        Returns:
            bool: 参加に成功した場合はTrue
        """
        try:
            # 既に参加している場合は何もしない
            if chain_id in self.active_microchains:
                return True
            
            # マイクロチェーンを取得
            chain = self.microchain_manager.get_chain(chain_id)
            
            if not chain:
                logger.warning(f"Microchain not found: {chain_id}")
                return False
            
            # 参加ノードとして自分自身を追加
            chain.add_participating_node(self.node_id)
            
            # アクティブなマイクロチェーンに追加
            self.active_microchains[chain_id] = chain
            
            logger.info(f"Joined microchain: {chain_id}")
            
            return True
            
        except Exception as e:
            logger.error(f"Error joining microchain: {e}")
            return False
    
    def _leave_microchain(self, chain_id: str) -> bool:
        """
        マイクロチェーンから離脱
        
        Args:
            chain_id: 離脱するマイクロチェーンのID
            
        Returns:
            bool: 離脱に成功した場合はTrue
        """
        try:
            # 参加していない場合は何もしない
            if chain_id not in self.active_microchains:
                return True
            
            # マイクロチェーンを取得
            chain = self.active_microchains[chain_id]
            
            # 参加ノードから自分自身を削除
            chain.remove_participating_node(self.node_id)
            
            # アクティブなマイクロチェーンから削除
            del self.active_microchains[chain_id]
            
            logger.info(f"Left microchain: {chain_id}")
            
            return True
            
        except Exception as e:
            logger.error(f"Error leaving microchain: {e}")
            return False