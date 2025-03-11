"""
PulseChainノードのAPIサーバー
"""

import json
import logging
from typing import Dict, Any, List, Optional
from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel
from ..core.node import Node
from ..core.transaction import Transaction
from ..consensus.environmental import EnvironmentalData


# ロガーの設定
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("PulseChainAPI")


# リクエスト/レスポンスモデル
class TransactionRequest(BaseModel):
    recipient: str
    amount: float
    data: Optional[Dict[str, Any]] = None


class TransactionResponse(BaseModel):
    hash: str
    sender: str
    recipient: str
    amount: float
    timestamp: float
    data: Optional[Dict[str, Any]] = None


class EnvironmentalDataRequest(BaseModel):
    temperature: float = 0.0
    humidity: float = 0.0
    pressure: float = 0.0
    light: float = 0.0
    sound: float = 0.0
    vibration: float = 0.0
    source_id: str = "api"


class NodeInfoResponse(BaseModel):
    node_id: str
    address: str
    is_leader: bool
    tx_pool_size: int
    processed_tx_count: int


# APIサーバークラス
class APIServer:
    """PulseChainノードのAPIサーバー"""
    
    def __init__(self, node: Node):
        """
        APIサーバーの初期化
        
        Args:
            node: APIを提供するノード
        """
        self.node = node
        self.app = FastAPI(title="PulseChain API", 
                          description="PulseChainノードのAPI",
                          version="0.1.0")
        
        # ルートの設定
        self._setup_routes()
    
    def _setup_routes(self) -> None:
        """APIルートの設定"""
        
        @self.app.get("/")
        async def root():
            return {"message": "Welcome to PulseChain API"}
        
        @self.app.get("/node/info", response_model=NodeInfoResponse)
        async def get_node_info():
            return {
                "node_id": self.node.node_id,
                "address": self.node.address,
                "is_leader": self.node.is_leader,
                "tx_pool_size": self.node.tx_pool.size(),
                "processed_tx_count": len(self.node.processed_tx_cache)
            }
        
        @self.app.post("/transactions", response_model=TransactionResponse)
        async def create_transaction(tx_request: TransactionRequest):
            try:
                # トランザクションの作成
                tx = self.node.create_transaction(
                    recipient=tx_request.recipient,
                    amount=tx_request.amount,
                    data=tx_request.data
                )
                
                return {
                    "hash": tx.hash,
                    "sender": tx.sender,
                    "recipient": tx.recipient,
                    "amount": tx.amount,
                    "timestamp": tx.timestamp,
                    "data": tx.data
                }
            except Exception as e:
                logger.error(f"Error creating transaction: {e}")
                raise HTTPException(status_code=400, detail=str(e))
        
        @self.app.get("/transactions", response_model=List[TransactionResponse])
        async def get_transactions():
            # プール内のすべてのトランザクションを取得
            transactions = self.node.tx_pool.get_all_transactions()
            
            return [
                {
                    "hash": tx.hash,
                    "sender": tx.sender,
                    "recipient": tx.recipient,
                    "amount": tx.amount,
                    "timestamp": tx.timestamp,
                    "data": tx.data
                }
                for tx in transactions
            ]
        
        @self.app.get("/transactions/{tx_hash}", response_model=Optional[TransactionResponse])
        async def get_transaction(tx_hash: str):
            # トランザクションの取得
            tx = self.node.tx_pool.get_transaction(tx_hash)
            
            if not tx:
                raise HTTPException(status_code=404, detail="Transaction not found")
            
            return {
                "hash": tx.hash,
                "sender": tx.sender,
                "recipient": tx.recipient,
                "amount": tx.amount,
                "timestamp": tx.timestamp,
                "data": tx.data
            }
        
        @self.app.post("/environmental-data")
        async def add_environmental_data(data_request: EnvironmentalDataRequest, 
                                        background_tasks: BackgroundTasks):
            # 環境データの作成
            env_data = EnvironmentalData(
                temperature=data_request.temperature,
                humidity=data_request.humidity,
                pressure=data_request.pressure,
                light=data_request.light,
                sound=data_request.sound,
                vibration=data_request.vibration,
                source_id=data_request.source_id
            )
            
            # バックグラウンドでデータを追加
            background_tasks.add_task(self.node.add_environmental_data, env_data)
            
            return {"status": "success", "message": "Environmental data added"}
    
    def run(self, host: str = "0.0.0.0", port: int = 8000):
        """
        APIサーバーを実行
        
        Args:
            host: サーバーのホスト
            port: サーバーのポート
        """
        import uvicorn
        uvicorn.run(self.app, host=host, port=port)