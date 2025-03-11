"""
分散型データソースから環境データを取得するモジュール
"""

import time
import random
import requests
import hashlib
import logging
from typing import List, Dict, Any, Optional
from ..consensus.environmental import EnvironmentalData

# ロガーの設定
logger = logging.getLogger("DistributedDataSource")

class DistributedDataSource:
    """複数のデータソースから環境データを取得するクラス"""
    
    def __init__(self):
        """分散型データソースの初期化"""
        self.last_bitcoin_block_hash = ""
        self.last_update_time = 0
    
    def get_combined_environmental_data(self) -> Optional[EnvironmentalData]:
        """
        複数のデータソースから環境データを取得して組み合わせる
        
        Returns:
            Optional[EnvironmentalData]: 組み合わせた環境データ、エラー時はNone
        """
        try:
            # 各データソースからデータを取得
            bitcoin_data = self._get_bitcoin_data()
            stock_data = self._get_stock_market_data()
            earthquake_data = self._get_earthquake_data()
            
            # データを組み合わせて環境データを作成
            env_data = EnvironmentalData(
                temperature=stock_data.get("temperature", 0.0),
                humidity=bitcoin_data.get("humidity", 0.0),
                pressure=earthquake_data.get("pressure", 0.0),
                light=stock_data.get("light", 0.0),
                sound=earthquake_data.get("sound", 0.0),
                vibration=earthquake_data.get("vibration", 0.0),
                source_id="distributed-source"
            )
            
            return env_data
            
        except Exception as e:
            logger.error(f"Error getting combined environmental data: {e}")
            return None
    
    def _get_bitcoin_data(self) -> Dict[str, float]:
        """
        Bitcoinブロックチェーンからデータを取得し、環境データに変換
        
        Returns:
            Dict[str, float]: 環境データの一部
        """
        try:
            # 10分ごとに更新（Bitcoinブロックの生成間隔に近い）
            current_time = time.time()
            if current_time - self.last_update_time < 600:
                # 前回のハッシュを再利用
                block_hash = self.last_bitcoin_block_hash
            else:
                # 最新のBitcoinブロックハッシュを取得
                response = requests.get("https://blockchain.info/latestblock", timeout=10)
                response.raise_for_status()
                data = response.json()
                block_hash = data.get("hash", "")
                self.last_bitcoin_block_hash = block_hash
                self.last_update_time = current_time
            
            if not block_hash:
                return {"humidity": 50.0}
            
            # ハッシュを数値に変換
            hash_bytes = bytes.fromhex(block_hash)
            hash_int = int.from_bytes(hash_bytes[:4], byteorder='big')
            
            # 湿度に変換（0〜100%）
            humidity = (hash_int % 10000) / 100.0
            
            return {"humidity": humidity}
            
        except Exception as e:
            logger.error(f"Error getting Bitcoin data: {e}")
            return {"humidity": 50.0}
    
    def _get_stock_market_data(self) -> Dict[str, float]:
        """
        株式市場のデータを取得し、環境データに変換
        
        Returns:
            Dict[str, float]: 環境データの一部
        """
        try:
            # Alpha Vantage APIを使用（無料版は1分あたり5リクエストまで）
            # 実際の実装では、APIキーが必要
            # ここではランダムなデータを生成
            
            # 現在の時間に基づいて擬似的な株価を生成
            hour = time.localtime().tm_hour
            minute = time.localtime().tm_min
            
            # 取引時間内かどうかで変動を変える
            is_trading_hours = 9 <= hour <= 15
            
            # 基準温度（摂氏）：取引時間内は高め、それ以外は低め
            base_temp = 25.0 if is_trading_hours else 15.0
            
            # 分に基づく変動（0〜10度）
            temp_variation = (minute / 60.0) * 10.0
            
            # 最終的な温度
            temperature = base_temp + temp_variation
            
            # 光量：時間帯に基づいて変化
            if 6 <= hour < 18:  # 日中
                # 正午に最大になるようにする
                noon_distance = abs(hour - 12) + minute / 60.0
                light_factor = 1.0 - (noon_distance / 6.0)
                light = light_factor * 100000.0
            else:  # 夜間
                light = 0.0
            
            return {
                "temperature": temperature,
                "light": light
            }
            
        except Exception as e:
            logger.error(f"Error getting stock market data: {e}")
            return {"temperature": 20.0, "light": 50000.0}
    
    def _get_earthquake_data(self) -> Dict[str, float]:
        """
        地震データを取得し、環境データに変換
        
        Returns:
            Dict[str, float]: 環境データの一部
        """
        try:
            # USGS Earthquake APIを使用
            url = "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/all_hour.geojson"
            
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            features = data.get("features", [])
            
            # 地震の数と最大マグニチュード
            earthquake_count = len(features)
            max_magnitude = 0.0
            
            for feature in features:
                magnitude = feature.get("properties", {}).get("mag", 0.0)
                if magnitude > max_magnitude:
                    max_magnitude = magnitude
            
            # 気圧：地震の数に基づいて変動（基準は1013.25 hPa）
            pressure = 1013.25 + (earthquake_count * 0.5)
            
            # 音量：最大マグニチュードに基づいて変動（0〜100 dB）
            sound = max_magnitude * 10.0
            
            # 振動：最大マグニチュードに基づいて変動（0〜10 m/s²）
            vibration = max_magnitude / 10.0
            
            return {
                "pressure": pressure,
                "sound": sound,
                "vibration": vibration
            }
            
        except Exception as e:
            logger.error(f"Error getting earthquake data: {e}")
            return {"pressure": 1013.25, "sound": 0.0, "vibration": 0.0}