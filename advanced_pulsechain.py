"""
高度なPulseChainノードのメインアプリケーション
"""

import os
import time
import logging
import argparse
import threading
import random
from pulsechain.core.node import Node
from pulsechain.network.api_server import APIServer
from pulsechain.network.browser_data_collector import BrowserDataCollector
from pulsechain.consensus.environmental import EnvironmentalData
from pulsechain.utils.weather_api import WeatherDataProvider
from pulsechain.utils.distributed_data_source import DistributedDataSource
from pulsechain.utils.energy_optimizer import EnergyOptimizer
from pulsechain.core.trust_system import TrustSystem


# ロガーの設定
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("AdvancedPulseChain")


class AdvancedPulseChainNode:
    """高度なPulseChainノード - すべての機能を統合"""
    
    def __init__(self, options: dict):
        """
        高度なPulseChainノードの初期化
        
        Args:
            options: 設定オプション
        """
        self.options = options
        
        # ノードの作成
        self.node = Node(
            node_id=options.get("node_id"),
            use_quantum_crypto=options.get("use_quantum_crypto", True)
        )
        
        # データソースの初期化
        self.weather_provider = WeatherDataProvider(api_key=options.get("weather_api_key"))
        self.distributed_source = DistributedDataSource()
        self.browser_collector = BrowserDataCollector()
        
        # エネルギーオプティマイザーの初期化
        self.energy_optimizer = EnergyOptimizer(target_cpu_usage=options.get("target_cpu_usage", 30.0))
        
        # エネルギーオプティマイザーにスロットリングコールバックを登録
        self.energy_optimizer.register_throttle_callback(self.node.set_throttle_rate)
        
        # APIサーバーの作成
        self.api_server = APIServer(self.node)
        
        # ブラウザデータコレクターのルーターを追加
        self.api_server.app.include_router(self.browser_collector.router)
        
        # 信頼システムのAPIエンドポイントを追加
        self._setup_trust_api()
        
        # マイクロチェーンのAPIエンドポイントを追加
        self._setup_microchain_api()
        
        # スレッド
        self.data_collection_thread = None
        self.running = False
    
    def start(self):
        """ノードを起動"""
        if self.running:
            return
        
        self.running = True
        
        # ノードの起動
        self.node.start()
        
        # エネルギーオプティマイザーの起動
        self.energy_optimizer.start()
        
        # データ収集スレッドの開始
        self.data_collection_thread = threading.Thread(target=self._collect_environmental_data)
        self.data_collection_thread.daemon = True
        self.data_collection_thread.start()
        
        logger.info("Advanced PulseChain Node started")
        
        # APIサーバーの実行
        self.api_server.run(
            host=self.options.get("host", "0.0.0.0"),
            port=self.options.get("port", 52964)
        )
    
    def stop(self):
        """ノードを停止"""
        self.running = False
        
        # エネルギーオプティマイザーの停止
        self.energy_optimizer.stop()
        
        # ノードの停止
        self.node.stop()
        
        # データ収集スレッドの終了を待機
        if self.data_collection_thread:
            self.data_collection_thread.join(timeout=2.0)
        
        logger.info("Advanced PulseChain Node stopped")
    
    def _setup_trust_api(self):
        """信頼システムのAPIエンドポイントを設定"""
        from fastapi import HTTPException
        from pydantic import BaseModel
        
        class VoteRequest(BaseModel):
            target_id: str
            vote_value: float
        
        @self.api_server.app.get("/trust/scores")
        async def get_trust_scores():
            """すべてのノードの信頼スコアを取得"""
            return self.node.trust_system.get_all_scores()
        
        @self.api_server.app.get("/trust/trusted-nodes")
        async def get_trusted_nodes(min_reliability: float = 0.7):
            """信頼性の高いノードのリストを取得"""
            return {
                "trusted_nodes": self.node.trust_system.get_trusted_nodes(min_reliability)
            }
        
        @self.api_server.app.post("/trust/vote")
        async def submit_vote(vote_request: VoteRequest):
            """ノードに対する投票を提出"""
            success = self.node.trust_system.submit_vote(
                self.node.node_id,
                vote_request.target_id,
                vote_request.vote_value
            )
            
            if not success:
                raise HTTPException(status_code=400, detail="Vote submission failed")
            
            return {"status": "success", "message": "Vote submitted successfully"}
    
    def _setup_microchain_api(self):
        """マイクロチェーンのAPIエンドポイントを設定"""
        from fastapi import HTTPException
        from pydantic import BaseModel
        
        class MicrochainRequest(BaseModel):
            purpose: str
            ttl: float = 300.0
        
        @self.api_server.app.get("/microchains")
        async def get_microchains():
            """すべてのマイクロチェーンの情報を取得"""
            return self.node.microchain_manager.get_stats()
        
        @self.api_server.app.get("/microchains/active")
        async def get_active_microchains():
            """アクティブなマイクロチェーンの情報を取得"""
            return {
                "active_microchains": [
                    chain.get_stats() for chain in self.node.active_microchains.values()
                ]
            }
        
        @self.api_server.app.post("/microchains/create")
        async def create_microchain(request: MicrochainRequest):
            """新しいマイクロチェーンを作成"""
            chain_id = self.node._create_microchain(request.purpose)
            
            if not chain_id:
                raise HTTPException(status_code=400, detail="Failed to create microchain")
            
            return {"status": "success", "chain_id": chain_id}
        
        @self.api_server.app.post("/microchains/{chain_id}/join")
        async def join_microchain(chain_id: str):
            """マイクロチェーンに参加"""
            success = self.node._join_microchain(chain_id)
            
            if not success:
                raise HTTPException(status_code=400, detail="Failed to join microchain")
            
            return {"status": "success", "message": f"Joined microchain {chain_id}"}
        
        @self.api_server.app.post("/microchains/{chain_id}/leave")
        async def leave_microchain(chain_id: str):
            """マイクロチェーンから離脱"""
            success = self.node._leave_microchain(chain_id)
            
            if not success:
                raise HTTPException(status_code=400, detail="Failed to leave microchain")
            
            return {"status": "success", "message": f"Left microchain {chain_id}"}
    
    def _collect_environmental_data(self):
        """環境データを収集"""
        interval = self.options.get("data_interval", 5.0)
        
        while self.running:
            try:
                # 各データソースからデータを収集
                self._collect_from_weather_api()
                self._collect_from_distributed_source()
                self._collect_from_browser()
                
                # 省エネモードの場合は間隔を長くする
                if self.node.energy_saving_mode:
                    time.sleep(interval * 2)
                else:
                    time.sleep(interval)
                
            except Exception as e:
                logger.error(f"Error collecting environmental data: {e}")
                time.sleep(1.0)
    
    def _collect_from_weather_api(self):
        """気象APIからデータを収集"""
        if not self.options.get("use_weather_api", True):
            return
        
        try:
            # Open-Meteo APIからデータを取得
            env_data = self.weather_provider.get_open_meteo_data()
            
            if env_data:
                self.node.add_environmental_data(env_data)
                logger.debug(f"Added weather data from Open-Meteo API")
                return
            
            # OpenWeatherMap APIからデータを取得（APIキーがある場合）
            if self.options.get("weather_api_key"):
                env_data = self.weather_provider.get_openweathermap_data()
                
                if env_data:
                    self.node.add_environmental_data(env_data)
                    logger.debug(f"Added weather data from OpenWeatherMap API")
                    return
            
        except Exception as e:
            logger.error(f"Error collecting weather data: {e}")
    
    def _collect_from_distributed_source(self):
        """分散型データソースからデータを収集"""
        if not self.options.get("use_distributed_source", True):
            return
        
        try:
            env_data = self.distributed_source.get_combined_environmental_data()
            
            if env_data:
                self.node.add_environmental_data(env_data)
                logger.debug(f"Added data from distributed sources")
            
        except Exception as e:
            logger.error(f"Error collecting distributed data: {e}")
    
    def _collect_from_browser(self):
        """ブラウザからデータを収集"""
        if not self.options.get("use_browser_data", True):
            return
        
        try:
            env_data = self.browser_collector.get_environmental_data()
            
            if env_data:
                self.node.add_environmental_data(env_data)
                logger.debug(f"Added data from browser")
            
        except Exception as e:
            logger.error(f"Error collecting browser data: {e}")


def main():
    """メイン関数"""
    parser = argparse.ArgumentParser(description="Advanced PulseChain Node")
    parser.add_argument("--port", type=int, default=52964, help="API server port")
    parser.add_argument("--host", type=str, default="0.0.0.0", help="API server host")
    parser.add_argument("--node-id", type=str, help="Node ID (optional)")
    
    # 環境データ収集オプション
    parser.add_argument("--weather-api-key", type=str, help="OpenWeatherMap API key")
    parser.add_argument("--no-weather-api", action="store_true", help="Disable weather API data source")
    parser.add_argument("--no-distributed-source", action="store_true", help="Disable distributed data source")
    parser.add_argument("--no-browser-data", action="store_true", help="Disable browser data collection")
    parser.add_argument("--data-interval", type=float, default=5.0, 
                        help="Environmental data collection interval (seconds)")
    
    # エネルギー最適化オプション
    parser.add_argument("--target-cpu-usage", type=float, default=30.0,
                        help="Target CPU usage percentage (default: 30.0)")
    
    # 暗号化オプション
    parser.add_argument("--no-quantum-crypto", action="store_true",
                        help="Disable quantum-resistant cryptography")
    
    args = parser.parse_args()
    
    # オプションの設定
    options = {
        "port": args.port,
        "host": args.host,
        "node_id": args.node_id,
        "weather_api_key": args.weather_api_key,
        "use_weather_api": not args.no_weather_api,
        "use_distributed_source": not args.no_distributed_source,
        "use_browser_data": not args.no_browser_data,
        "data_interval": args.data_interval,
        "target_cpu_usage": args.target_cpu_usage,
        "use_quantum_crypto": not args.no_quantum_crypto
    }
    
    try:
        # 高度なPulseChainノードの作成と起動
        node = AdvancedPulseChainNode(options)
        node.start()
        
    except KeyboardInterrupt:
        logger.info("Shutting down...")
    except Exception as e:
        logger.error(f"Error: {e}")
    finally:
        # ノードの停止
        if 'node' in locals():
            node.stop()


if __name__ == "__main__":
    main()