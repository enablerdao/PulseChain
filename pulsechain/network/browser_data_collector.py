"""
ブラウザからの環境データ収集モジュール
"""

import time
import json
import logging
from typing import Dict, Any, Optional
from fastapi import APIRouter, Request, Response
from pydantic import BaseModel
from ..consensus.environmental import EnvironmentalData

# ロガーの設定
logger = logging.getLogger("BrowserDataCollector")

class BrowserEnvironmentalData(BaseModel):
    """ブラウザから収集する環境データモデル"""
    battery_level: float = 0.0
    network_type: str = "unknown"
    connection_speed: float = 0.0
    device_orientation: Dict[str, float] = {}
    ambient_light: Optional[float] = None
    device_motion: Dict[str, float] = {}
    geolocation: Optional[Dict[str, float]] = None
    timestamp: float = 0.0
    user_agent: str = ""
    screen_info: Dict[str, int] = {}

class BrowserDataCollector:
    """ブラウザからの環境データ収集クラス"""
    
    def __init__(self):
        """ブラウザデータコレクターの初期化"""
        self.router = APIRouter()
        self._setup_routes()
        self.latest_data: Dict[str, BrowserEnvironmentalData] = {}
    
    def _setup_routes(self):
        """APIルートの設定"""
        
        @self.router.post("/browser-data")
        async def collect_browser_data(data: BrowserEnvironmentalData, request: Request):
            """ブラウザからの環境データを収集"""
            client_ip = request.client.host
            self.latest_data[client_ip] = data
            logger.debug(f"Received browser data from {client_ip}")
            return {"status": "success"}
        
        @self.router.get("/browser-collector.js")
        async def get_collector_script():
            """ブラウザデータ収集用のJavaScriptを提供"""
            js_code = """
// PulseChain Browser Environmental Data Collector
(function() {
    // 収集する環境データ
    const environmentalData = {
        battery_level: 0,
        network_type: 'unknown',
        connection_speed: 0,
        device_orientation: {},
        ambient_light: null,
        device_motion: {},
        geolocation: null,
        timestamp: Date.now() / 1000,
        user_agent: navigator.userAgent,
        screen_info: {
            width: window.screen.width,
            height: window.screen.height,
            colorDepth: window.screen.colorDepth
        }
    };

    // バッテリー情報の取得
    if ('getBattery' in navigator) {
        navigator.getBattery().then(function(battery) {
            environmentalData.battery_level = battery.level * 100;
            
            // バッテリー状態の変化を監視
            battery.addEventListener('levelchange', function() {
                environmentalData.battery_level = battery.level * 100;
            });
        });
    }

    // ネットワーク情報の取得
    if ('connection' in navigator) {
        const connection = navigator.connection;
        environmentalData.network_type = connection.type;
        environmentalData.connection_speed = connection.downlink;
        
        // ネットワーク状態の変化を監視
        connection.addEventListener('change', function() {
            environmentalData.network_type = connection.type;
            environmentalData.connection_speed = connection.downlink;
        });
    }

    // デバイスの向きの取得
    window.addEventListener('deviceorientation', function(event) {
        environmentalData.device_orientation = {
            alpha: event.alpha, // z軸周りの回転（0-360度）
            beta: event.beta,   // x軸周りの回転（-180-180度）
            gamma: event.gamma  // y軸周りの回転（-90-90度）
        };
    });

    // 環境光センサーの取得
    if ('AmbientLightSensor' in window) {
        try {
            const sensor = new AmbientLightSensor();
            sensor.addEventListener('reading', function() {
                environmentalData.ambient_light = sensor.illuminance;
            });
            sensor.start();
        } catch (error) {
            console.error('Ambient Light Sensor not available:', error);
        }
    }

    // デバイスの動きの取得
    window.addEventListener('devicemotion', function(event) {
        environmentalData.device_motion = {
            acceleration_x: event.acceleration.x,
            acceleration_y: event.acceleration.y,
            acceleration_z: event.acceleration.z,
            rotation_rate_alpha: event.rotationRate.alpha,
            rotation_rate_beta: event.rotationRate.beta,
            rotation_rate_gamma: event.rotationRate.gamma
        };
    });

    // 位置情報の取得（ユーザーの許可が必要）
    if ('geolocation' in navigator) {
        navigator.geolocation.getCurrentPosition(function(position) {
            environmentalData.geolocation = {
                latitude: position.coords.latitude,
                longitude: position.coords.longitude,
                altitude: position.coords.altitude,
                accuracy: position.coords.accuracy
            };
        });
    }

    // データを定期的に送信
    function sendData() {
        environmentalData.timestamp = Date.now() / 1000;
        
        fetch('/browser-data', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(environmentalData)
        })
        .then(response => response.json())
        .then(data => console.log('Data sent successfully:', data))
        .catch(error => console.error('Error sending data:', error));
        
        // 10秒ごとに送信
        setTimeout(sendData, 10000);
    }

    // 初回送信
    sendData();
})();
            """
            return Response(content=js_code, media_type="application/javascript")
    
    def get_environmental_data(self) -> Optional[EnvironmentalData]:
        """
        ブラウザから収集したデータを環境データに変換
        
        Returns:
            Optional[EnvironmentalData]: 変換した環境データ、データがない場合はNone
        """
        if not self.latest_data:
            return None
        
        # 最新のデータを使用
        latest_ip = max(self.latest_data.keys(), key=lambda ip: self.latest_data[ip].timestamp)
        browser_data = self.latest_data[latest_ip]
        
        # 環境データに変換
        env_data = EnvironmentalData(
            # バッテリーレベルを温度として使用
            temperature=browser_data.battery_level,
            # 接続速度を湿度として使用
            humidity=browser_data.connection_speed * 10.0,
            # スクリーンの色深度を気圧として使用
            pressure=1000.0 + browser_data.screen_info.get("colorDepth", 24),
            # 環境光センサーの値を光量として使用
            light=browser_data.ambient_light or 0.0,
            # デバイスの動きの大きさを音量として使用
            sound=self._calculate_motion_magnitude(browser_data.device_motion),
            # デバイスの向きの変化を振動として使用
            vibration=self._calculate_orientation_change(browser_data.device_orientation),
            source_id=f"browser-{latest_ip}"
        )
        
        return env_data
    
    def _calculate_motion_magnitude(self, motion: Dict[str, float]) -> float:
        """
        デバイスの動きの大きさを計算
        
        Args:
            motion: デバイスの動きデータ
            
        Returns:
            float: 動きの大きさ（0.0〜100.0）
        """
        if not motion:
            return 0.0
        
        # 加速度の大きさを計算
        accel_x = motion.get("acceleration_x", 0.0) or 0.0
        accel_y = motion.get("acceleration_y", 0.0) or 0.0
        accel_z = motion.get("acceleration_z", 0.0) or 0.0
        
        magnitude = (accel_x ** 2 + accel_y ** 2 + accel_z ** 2) ** 0.5
        
        # 0〜100の範囲に正規化
        return min(magnitude * 10.0, 100.0)
    
    def _calculate_orientation_change(self, orientation: Dict[str, float]) -> float:
        """
        デバイスの向きの変化を計算
        
        Args:
            orientation: デバイスの向きデータ
            
        Returns:
            float: 向きの変化（0.0〜10.0）
        """
        if not orientation:
            return 0.0
        
        # 向きの値を取得
        alpha = orientation.get("alpha", 0.0) or 0.0
        beta = orientation.get("beta", 0.0) or 0.0
        gamma = orientation.get("gamma", 0.0) or 0.0
        
        # 値の大きさを計算
        magnitude = (alpha ** 2 + beta ** 2 + gamma ** 2) ** 0.5
        
        # 0〜10の範囲に正規化
        return min(magnitude / 36.0, 10.0)