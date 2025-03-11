"""
リアルタイムトランザクション処理のためのトランザクションプール
"""

import time
import threading
from typing import Dict, List, Optional, Callable
from .transaction import Transaction


class TransactionPool:
    """トランザクションプール - 未処理のトランザクションを管理"""
    
    def __init__(self, max_size: int = 10000):
        """
        トランザクションプールの初期化
        
        Args:
            max_size: プールの最大サイズ
        """
        self.transactions: Dict[str, Transaction] = {}  # ハッシュをキーとするトランザクション
        self.max_size = max_size
        self.lock = threading.RLock()  # スレッドセーフな操作のためのロック
    
    def add_transaction(self, transaction: Transaction) -> bool:
        """
        トランザクションをプールに追加
        
        Args:
            transaction: 追加するトランザクション
            
        Returns:
            bool: 追加に成功した場合はTrue、そうでない場合はFalse
        """
        with self.lock:
            # プールが満杯の場合
            if len(self.transactions) >= self.max_size:
                return False
            
            # トランザクションが既に存在する場合
            if transaction.hash in self.transactions:
                return False
            
            # トランザクションの署名を検証
            if not transaction.verify():
                return False
            
            # トランザクションをプールに追加
            self.transactions[transaction.hash] = transaction
            return True
    
    def remove_transaction(self, tx_hash: str) -> Optional[Transaction]:
        """
        トランザクションをプールから削除
        
        Args:
            tx_hash: 削除するトランザクションのハッシュ
            
        Returns:
            Optional[Transaction]: 削除されたトランザクション、存在しない場合はNone
        """
        with self.lock:
            return self.transactions.pop(tx_hash, None)
    
    def get_transaction(self, tx_hash: str) -> Optional[Transaction]:
        """
        ハッシュからトランザクションを取得
        
        Args:
            tx_hash: 取得するトランザクションのハッシュ
            
        Returns:
            Optional[Transaction]: 取得されたトランザクション、存在しない場合はNone
        """
        return self.transactions.get(tx_hash)
    
    def get_all_transactions(self) -> List[Transaction]:
        """
        すべてのトランザクションを取得
        
        Returns:
            List[Transaction]: プール内のすべてのトランザクション
        """
        with self.lock:
            return list(self.transactions.values())
    
    def clear(self) -> None:
        """プールをクリア"""
        with self.lock:
            self.transactions.clear()
    
    def size(self) -> int:
        """
        プールのサイズを取得
        
        Returns:
            int: プール内のトランザクション数
        """
        return len(self.transactions)
    
    def process_transactions(self, processor: Callable[[Transaction], bool], 
                             max_count: Optional[int] = None) -> List[Transaction]:
        """
        トランザクションを処理
        
        Args:
            processor: トランザクションを処理する関数。成功した場合はTrue、失敗した場合はFalseを返す
            max_count: 処理するトランザクションの最大数（Noneの場合はすべて処理）
            
        Returns:
            List[Transaction]: 処理に成功したトランザクションのリスト
        """
        processed = []
        
        with self.lock:
            # 処理するトランザクションのリストを作成
            txs_to_process = list(self.transactions.values())
            if max_count is not None:
                txs_to_process = txs_to_process[:max_count]
            
            # トランザクションを処理
            for tx in txs_to_process:
                if processor(tx):
                    processed.append(tx)
                    self.transactions.pop(tx.hash, None)
        
        return processed