"""
ダイナミックマイクロチェーン構造の実装
"""

import time
import uuid
import logging
import threading
from typing import Dict, List, Set, Optional, Any, Callable
from .transaction import Transaction
from .transaction_pool import TransactionPool

# ロガーの設定
logger = logging.getLogger("MicroChain")


class MicroChain:
    """マイクロチェーン - 一時的かつ動的に生成・消滅するチェーン"""
    
    def __init__(self, chain_id: Optional[str] = None, 
                 purpose: str = "general", 
                 ttl: float = 300.0):
        """
        マイクロチェーンの初期化
        
        Args:
            chain_id: チェーンID（指定がなければ自動生成）
            purpose: チェーンの目的
            ttl: 生存時間（秒）
        """
        self.chain_id = chain_id or str(uuid.uuid4())
        self.purpose = purpose
        self.creation_time = time.time()
        self.ttl = ttl
        self.expiration_time = self.creation_time + ttl
        self.tx_pool = TransactionPool(max_size=1000)
        self.processed_transactions: List[Transaction] = []
        self.participating_nodes: Set[str] = set()
        self.is_active = True
        self.lock = threading.RLock()
        
        logger.info(f"MicroChain {self.chain_id} created for purpose: {purpose}, TTL: {ttl}s")
    
    def add_transaction(self, tx: Transaction) -> bool:
        """
        トランザクションを追加
        
        Args:
            tx: 追加するトランザクション
            
        Returns:
            bool: 追加に成功した場合はTrue
        """
        with self.lock:
            if not self.is_active or time.time() > self.expiration_time:
                self.is_active = False
                return False
            
            return self.tx_pool.add_transaction(tx)
    
    def process_transactions(self, processor: Callable[[Transaction], bool], 
                             max_count: Optional[int] = None) -> List[Transaction]:
        """
        トランザクションを処理
        
        Args:
            processor: トランザクションを処理する関数
            max_count: 処理するトランザクションの最大数
            
        Returns:
            List[Transaction]: 処理されたトランザクションのリスト
        """
        with self.lock:
            if not self.is_active:
                return []
            
            processed = self.tx_pool.process_transactions(processor, max_count)
            self.processed_transactions.extend(processed)
            return processed
    
    def add_participating_node(self, node_id: str) -> None:
        """
        参加ノードを追加
        
        Args:
            node_id: ノードID
        """
        with self.lock:
            self.participating_nodes.add(node_id)
    
    def remove_participating_node(self, node_id: str) -> None:
        """
        参加ノードを削除
        
        Args:
            node_id: ノードID
        """
        with self.lock:
            self.participating_nodes.discard(node_id)
    
    def extend_ttl(self, additional_time: float) -> None:
        """
        生存時間を延長
        
        Args:
            additional_time: 追加する時間（秒）
        """
        with self.lock:
            self.ttl += additional_time
            self.expiration_time = self.creation_time + self.ttl
            logger.info(f"MicroChain {self.chain_id} TTL extended by {additional_time}s, new TTL: {self.ttl}s")
    
    def is_expired(self) -> bool:
        """
        チェーンが期限切れかどうかを確認
        
        Returns:
            bool: 期限切れの場合はTrue
        """
        return time.time() > self.expiration_time
    
    def deactivate(self) -> None:
        """チェーンを非アクティブ化"""
        with self.lock:
            self.is_active = False
            logger.info(f"MicroChain {self.chain_id} deactivated")
    
    def get_stats(self) -> Dict[str, Any]:
        """
        チェーンの統計情報を取得
        
        Returns:
            Dict[str, Any]: 統計情報
        """
        with self.lock:
            return {
                "chain_id": self.chain_id,
                "purpose": self.purpose,
                "creation_time": self.creation_time,
                "ttl": self.ttl,
                "expiration_time": self.expiration_time,
                "is_active": self.is_active,
                "is_expired": self.is_expired(),
                "pending_tx_count": self.tx_pool.size(),
                "processed_tx_count": len(self.processed_transactions),
                "participating_nodes": len(self.participating_nodes),
                "remaining_time": max(0, self.expiration_time - time.time())
            }


class MicroChainManager:
    """マイクロチェーンを管理するクラス"""
    
    def __init__(self, max_chains: int = 100):
        """
        マイクロチェーンマネージャーの初期化
        
        Args:
            max_chains: 同時に管理する最大チェーン数
        """
        self.chains: Dict[str, MicroChain] = {}
        self.max_chains = max_chains
        self.lock = threading.RLock()
        self.cleanup_thread = None
        self.running = False
    
    def start(self) -> None:
        """マネージャーを起動"""
        if self.running:
            return
        
        self.running = True
        
        # クリーンアップスレッドの開始
        self.cleanup_thread = threading.Thread(target=self._cleanup_loop)
        self.cleanup_thread.daemon = True
        self.cleanup_thread.start()
        
        logger.info("MicroChainManager started")
    
    def stop(self) -> None:
        """マネージャーを停止"""
        self.running = False
        
        if self.cleanup_thread:
            self.cleanup_thread.join(timeout=2.0)
        
        logger.info("MicroChainManager stopped")
    
    def create_chain(self, purpose: str = "general", ttl: float = 300.0) -> MicroChain:
        """
        新しいマイクロチェーンを作成
        
        Args:
            purpose: チェーンの目的
            ttl: 生存時間（秒）
            
        Returns:
            MicroChain: 作成されたマイクロチェーン
        """
        with self.lock:
            # チェーン数が上限に達している場合は古いチェーンを削除
            if len(self.chains) >= self.max_chains:
                self._remove_oldest_chain()
            
            # 新しいチェーンを作成
            chain = MicroChain(purpose=purpose, ttl=ttl)
            self.chains[chain.chain_id] = chain
            
            return chain
    
    def get_chain(self, chain_id: str) -> Optional[MicroChain]:
        """
        チェーンIDからマイクロチェーンを取得
        
        Args:
            chain_id: チェーンID
            
        Returns:
            Optional[MicroChain]: マイクロチェーン、存在しない場合はNone
        """
        with self.lock:
            return self.chains.get(chain_id)
    
    def get_chains_by_purpose(self, purpose: str) -> List[MicroChain]:
        """
        目的からマイクロチェーンを取得
        
        Args:
            purpose: チェーンの目的
            
        Returns:
            List[MicroChain]: マイクロチェーンのリスト
        """
        with self.lock:
            return [
                chain for chain in self.chains.values()
                if chain.purpose == purpose and chain.is_active
            ]
    
    def get_active_chains(self) -> List[MicroChain]:
        """
        アクティブなマイクロチェーンを取得
        
        Returns:
            List[MicroChain]: アクティブなマイクロチェーンのリスト
        """
        with self.lock:
            return [
                chain for chain in self.chains.values()
                if chain.is_active
            ]
    
    def remove_chain(self, chain_id: str) -> bool:
        """
        マイクロチェーンを削除
        
        Args:
            chain_id: チェーンID
            
        Returns:
            bool: 削除に成功した場合はTrue
        """
        with self.lock:
            if chain_id in self.chains:
                chain = self.chains[chain_id]
                chain.deactivate()
                del self.chains[chain_id]
                logger.info(f"MicroChain {chain_id} removed")
                return True
            return False
    
    def _remove_oldest_chain(self) -> None:
        """最も古いマイクロチェーンを削除"""
        with self.lock:
            if not self.chains:
                return
            
            # 作成時間が最も古いチェーンを見つける
            oldest_id = min(
                self.chains.keys(),
                key=lambda chain_id: self.chains[chain_id].creation_time
            )
            
            # チェーンを削除
            self.remove_chain(oldest_id)
    
    def _cleanup_expired_chains(self) -> None:
        """期限切れのマイクロチェーンをクリーンアップ"""
        with self.lock:
            expired_chains = [
                chain_id for chain_id, chain in self.chains.items()
                if chain.is_expired()
            ]
            
            for chain_id in expired_chains:
                self.remove_chain(chain_id)
            
            if expired_chains:
                logger.info(f"Cleaned up {len(expired_chains)} expired microchains")
    
    def _cleanup_loop(self) -> None:
        """クリーンアップループ - 定期的に期限切れのチェーンを削除"""
        while self.running:
            try:
                # 期限切れのチェーンをクリーンアップ
                self._cleanup_expired_chains()
                
                # 10秒ごとにクリーンアップ
                time.sleep(10.0)
                
            except Exception as e:
                logger.error(f"Error in cleanup loop: {e}")
                time.sleep(1.0)
    
    def get_stats(self) -> Dict[str, Any]:
        """
        マネージャーの統計情報を取得
        
        Returns:
            Dict[str, Any]: 統計情報
        """
        with self.lock:
            active_chains = [chain for chain in self.chains.values() if chain.is_active]
            expired_chains = [chain for chain in self.chains.values() if chain.is_expired()]
            
            return {
                "total_chains": len(self.chains),
                "active_chains": len(active_chains),
                "expired_chains": len(expired_chains),
                "max_chains": self.max_chains,
                "chains": [chain.get_stats() for chain in self.chains.values()]
            }