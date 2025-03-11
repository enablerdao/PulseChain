"""
リアルタイムトランザクション処理（RTCS）のトランザクションクラス
"""

import time
import json
import hashlib
from typing import Dict, Any, Optional
from ..crypto.signatures import sign_data, verify_signature


class Transaction:
    """トランザクションクラス - リアルタイム処理のための基本単位"""
    
    def __init__(self, 
                 sender: str, 
                 recipient: str, 
                 amount: float, 
                 data: Optional[Dict[str, Any]] = None,
                 timestamp: Optional[float] = None,
                 signature: Optional[str] = None,
                 tx_hash: Optional[str] = None):
        """
        トランザクションの初期化
        
        Args:
            sender: 送信者のアドレス
            recipient: 受信者のアドレス
            amount: 送金額
            data: 追加データ（スマートコントラクト呼び出しなど）
            timestamp: タイムスタンプ（指定がなければ現在時刻）
            signature: トランザクションの署名（検証時に使用）
            tx_hash: トランザクションのハッシュ（指定がなければ計算）
        """
        self.sender = sender
        self.recipient = recipient
        self.amount = amount
        self.data = data or {}
        self.timestamp = timestamp or time.time()
        self.signature = signature
        self._hash = tx_hash
        
    def to_dict(self) -> Dict[str, Any]:
        """トランザクションを辞書形式に変換"""
        return {
            "sender": self.sender,
            "recipient": self.recipient,
            "amount": self.amount,
            "data": self.data,
            "timestamp": self.timestamp,
            "signature": self.signature,
            "hash": self.hash
        }
    
    def to_json(self) -> str:
        """トランザクションをJSON形式に変換"""
        return json.dumps(self.to_dict(), sort_keys=True)
    
    @property
    def hash(self) -> str:
        """トランザクションのハッシュを計算または取得"""
        if self._hash is None:
            # 署名を除いたデータのハッシュを計算
            tx_data = {
                "sender": self.sender,
                "recipient": self.recipient,
                "amount": self.amount,
                "data": self.data,
                "timestamp": self.timestamp
            }
            tx_string = json.dumps(tx_data, sort_keys=True)
            self._hash = hashlib.sha256(tx_string.encode()).hexdigest()
        return self._hash
    
    def sign(self, private_key: str) -> None:
        """トランザクションに署名"""
        self.signature = sign_data(self.hash, private_key)
    
    def verify(self) -> bool:
        """トランザクションの署名を検証"""
        if not self.signature:
            return False
        return verify_signature(self.hash, self.signature, self.sender)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Transaction':
        """辞書からトランザクションを生成"""
        return cls(
            sender=data["sender"],
            recipient=data["recipient"],
            amount=data["amount"],
            data=data.get("data", {}),
            timestamp=data.get("timestamp"),
            signature=data.get("signature"),
            tx_hash=data.get("hash")
        )
    
    @classmethod
    def from_json(cls, json_str: str) -> 'Transaction':
        """JSON文字列からトランザクションを生成"""
        data = json.loads(json_str)
        return cls.from_dict(data)