"""
拡張版PulseChainノードのメインアプリケーション
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


# ロガーの設定
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("PulseChainEnhanced")


class EnhancedEnvironmentalDataCollector:
    """拡張版環境データコレクター"""
    
    def __init__(self, node: Node, options: dict):
        """
        拡張版環境データコレクターの初期化
        
        Args:
            node: データを追加するノード
            options: 設定オプション
        """
        self.node = node
        self.options = options
        self.running = False
        self.thread = None
        
        # データソースの初期化
        self.weather_provider = WeatherDataProvider(api_key=options.get("weather_api_key"))
        self.distributed_source = DistributedDataSource()
        self.browser_collector = BrowserDataCollector()
        
        # データソースの優先順位
        self.data_sources = []
        
        if options.get("use_weather_api", True):
            self.data_sources.append(self._get_weather_data)
        
        if options.get("use_distributed_source", True):
            self.data_sources.append(self._get_distributed_data)
        
        if options.get("use_browser_data", True):
            self.data_sources.append(self._get_browser_data)
        
        if options.get("use_simulation", True):
            self.data_sources.append(self._get_simulated_data)
    
    def start(self, interval: float = 5.0):
        """
        データ収集を開始
        
        Args:
            interval: データ収集の間隔（秒）
        """
        if self.running:
            return
        
        self.running = True
        self.thread = threading.Thread(target=self._collection_loop, args=(interval,))
        self.thread.daemon = True
        self.thread.start()
        
        logger.info("Enhanced environmental data collection started")
    
    def stop(self):
        """データ収集を停止"""
        self.running = False
        
        if self.thread:
            self.thread.join(timeout=2.0)
        
        logger.info("Enhanced environmental data collection stopped")
    
    def _collection_loop(self, interval: float):
        """
        データ収集ループ
        
        Args:
            interval: データ収集の間隔（秒）
        """
        while self.running:
            try:
                # 各データソースからデータを収集
                for source_func in self.data_sources:
                    env_data = source_func()
                    
                    if env_data:
                        # ノードに環境データを追加
                        self.node.add_environmental_data(env_data)
                        logger.debug(f"Added environmental data from {env_data.source_id}")
                
                # 指定された間隔でスリープ
                time.sleep(interval)
                
            except Exception as e:
                logger.error(f"Error in data collection loop: {e}")
                time.sleep(1.0)
    
    def _get_weather_data(self) -> EnvironmentalData:
        """
        気象APIからデータを取得
        
        Returns:
            EnvironmentalData: 取得した環境データ
        """
        try:
            # Open-Meteo APIからデータを取得
            env_data = self.weather_provider.get_open_meteo_data()
            
            if env_data:
                return env_data
            
            # OpenWeatherMap APIからデータを取得（APIキーがある場合）
            if self.options.get("weather_api_key"):
                env_data = self.weather_provider.get_openweathermap_data()
                
                if env_data:
                    return env_data
            
            # データが取得できなかった場合はシミュレーションデータを返す
            return self._get_simulated_data()
            
        except Exception as e:
            logger.error(f"Error getting weather data: {e}")
            return self._get_simulated_data()
    
    def _get_distributed_data(self) -> EnvironmentalData:
        """
        分散型データソースからデータを取得
        
        Returns:
            EnvironmentalData: 取得した環境データ
        """
        try:
            env_data = self.distributed_source.get_combined_environmental_data()
            
            if env_data:
                return env_data
            
            # データが取得できなかった場合はシミュレーションデータを返す
            return self._get_simulated_data()
            
        except Exception as e:
            logger.error(f"Error getting distributed data: {e}")
            return self._get_simulated_data()
    
    def _get_browser_data(self) -> EnvironmentalData:
        """
        ブラウザからのデータを取得
        
        Returns:
            EnvironmentalData: 取得した環境データ
        """
        try:
            env_data = self.browser_collector.get_environmental_data()
            
            if env_data:
                return env_data
            
            # データが取得できなかった場合はシミュレーションデータを返す
            return self._get_simulated_data()
            
        except Exception as e:
            logger.error(f"Error getting browser data: {e}")
            return self._get_simulated_data()
    
    def _get_simulated_data(self) -> EnvironmentalData:
        """
        シミュレーションデータを生成
        
        Returns:
            EnvironmentalData: 生成した環境データ
        """
        return EnvironmentalData.generate_random()


def main():
    """メイン関数"""
    parser = argparse.ArgumentParser(description="Enhanced PulseChain Node")
    parser.add_argument("--port", type=int, default=52964, help="API server port")
    parser.add_argument("--host", type=str, default="0.0.0.0", help="API server host")
    parser.add_argument("--node-id", type=str, help="Node ID (optional)")
    
    # 環境データ収集オプション
    parser.add_argument("--weather-api-key", type=str, help="OpenWeatherMap API key")
    parser.add_argument("--no-weather-api", action="store_true", help="Disable weather API data source")
    parser.add_argument("--no-distributed-source", action="store_true", help="Disable distributed data source")
    parser.add_argument("--no-browser-data", action="store_true", help="Disable browser data collection")
    parser.add_argument("--no-simulation", action="store_true", help="Disable simulated data")
    parser.add_argument("--data-interval", type=float, default=5.0, 
                        help="Environmental data collection interval (seconds)")
    
    args = parser.parse_args()
    
    try:
        # ノードの作成
        node = Node(node_id=args.node_id)
        
        # ノードの起動
        node.start()
        
        # 環境データ収集オプションの設定
        env_options = {
            "weather_api_key": args.weather_api_key,
            "use_weather_api": not args.no_weather_api,
            "use_distributed_source": not args.no_distributed_source,
            "use_browser_data": not args.no_browser_data,
            "use_simulation": not args.no_simulation
        }
        
        # 拡張版環境データコレクターの作成と開始
        collector = EnhancedEnvironmentalDataCollector(node, env_options)
        collector.start(interval=args.data_interval)
        
        # ブラウザデータコレクターのルーターを取得
        browser_router = collector.browser_collector.router
        
        # APIサーバーの作成と実行
        api_server = APIServer(node)
        
        # ブラウザデータコレクターのルーターを追加
        api_server.app.include_router(browser_router)
        
        # サーバーの実行
        api_server.run(host=args.host, port=args.port)
        
    except KeyboardInterrupt:
        logger.info("Shutting down...")
    except Exception as e:
        logger.error(f"Error: {e}")
    finally:
        # 環境データコレクターの停止
        if 'collector' in locals():
            collector.stop()
        
        # ノードの停止
        if 'node' in locals():
            node.stop()


if __name__ == "__main__":
    main()