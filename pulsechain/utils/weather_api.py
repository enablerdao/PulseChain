"""
公開気象APIから環境データを取得するモジュール
"""

import requests
import time
import logging
from typing import Dict, Any, Optional
from ..consensus.environmental import EnvironmentalData

# ロガーの設定
logger = logging.getLogger("WeatherAPI")

class WeatherDataProvider:
    """公開気象APIから環境データを取得するクラス"""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        気象データプロバイダの初期化
        
        Args:
            api_key: OpenWeatherMap APIキー（オプション）
        """
        self.api_key = api_key
    
    def get_open_meteo_data(self, latitude: float = 35.6895, longitude: float = 139.6917) -> Optional[EnvironmentalData]:
        """
        Open-Meteo APIから気象データを取得
        
        Args:
            latitude: 緯度（デフォルトは東京）
            longitude: 経度（デフォルトは東京）
            
        Returns:
            Optional[EnvironmentalData]: 取得した環境データ、エラー時はNone
        """
        try:
            url = f"https://api.open-meteo.com/v1/forecast?latitude={latitude}&longitude={longitude}&current=temperature_2m,relative_humidity_2m,surface_pressure,wind_speed_10m"
            
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            current = data.get("current", {})
            
            if not current:
                logger.error("No current weather data available")
                return None
            
            # 環境データの作成
            env_data = EnvironmentalData(
                temperature=current.get("temperature_2m", 0.0),
                humidity=current.get("relative_humidity_2m", 0.0),
                pressure=current.get("surface_pressure", 0.0),
                # 光量、音量、振動はAPIから取得できないため0に設定
                light=0.0,
                sound=0.0,
                vibration=current.get("wind_speed_10m", 0.0) / 10.0,  # 風速を振動の代わりに使用
                source_id="open-meteo-api"
            )
            
            return env_data
            
        except Exception as e:
            logger.error(f"Error fetching weather data: {e}")
            return None
    
    def get_openweathermap_data(self, city: str = "Tokyo") -> Optional[EnvironmentalData]:
        """
        OpenWeatherMap APIから気象データを取得
        
        Args:
            city: 都市名（デフォルトは東京）
            
        Returns:
            Optional[EnvironmentalData]: 取得した環境データ、エラー時はNone
        """
        if not self.api_key:
            logger.error("OpenWeatherMap API key is required")
            return None
        
        try:
            url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={self.api_key}&units=metric"
            
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            # 環境データの作成
            env_data = EnvironmentalData(
                temperature=data.get("main", {}).get("temp", 0.0),
                humidity=data.get("main", {}).get("humidity", 0.0),
                pressure=data.get("main", {}).get("pressure", 0.0),
                # 光量はAPIから取得できないため、時間帯に基づいて推定
                light=self._estimate_light_level(data.get("dt", 0), data.get("sys", {}).get("sunrise", 0), data.get("sys", {}).get("sunset", 0)),
                # 音量はAPIから取得できないため0に設定
                sound=0.0,
                # 振動は風速から推定
                vibration=data.get("wind", {}).get("speed", 0.0) / 10.0,
                source_id="openweathermap-api"
            )
            
            return env_data
            
        except Exception as e:
            logger.error(f"Error fetching OpenWeatherMap data: {e}")
            return None
    
    def _estimate_light_level(self, current_time: int, sunrise: int, sunset: int) -> float:
        """
        時間帯に基づいて光量レベルを推定
        
        Args:
            current_time: 現在のUNIXタイムスタンプ
            sunrise: 日の出のUNIXタイムスタンプ
            sunset: 日の入りのUNIXタイムスタンプ
            
        Returns:
            float: 推定光量レベル（0.0〜100000.0）
        """
        # 夜間
        if current_time < sunrise or current_time > sunset:
            return 0.0
        
        # 日中の時間の割合を計算（0.0〜1.0）
        day_length = sunset - sunrise
        time_since_sunrise = current_time - sunrise
        day_progress = time_since_sunrise / day_length if day_length > 0 else 0.5
        
        # 正午に最大になるような放物線を描く
        # 0.5で最大（正午）、0.0と1.0で最小（日の出と日の入り）
        light_factor = 1.0 - 4.0 * (day_progress - 0.5) ** 2
        
        # 最大光量を100000.0とする
        return light_factor * 100000.0