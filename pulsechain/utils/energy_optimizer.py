"""
エネルギー効率を最適化するモジュール
"""

import time
import threading
import logging
import psutil
import os
from typing import Dict, Any, List, Optional, Callable

# ロガーの設定
logger = logging.getLogger("EnergyOptimizer")

class EnergyOptimizer:
    """ノードのエネルギー効率を最適化するクラス"""
    
    def __init__(self, target_cpu_usage: float = 30.0):
        """
        エネルギーオプティマイザーの初期化
        
        Args:
            target_cpu_usage: 目標CPU使用率（%）
        """
        self.target_cpu_usage = target_cpu_usage
        self.running = False
        self.thread = None
        self.throttle_callbacks: List[Callable[[float], None]] = []
    
    def start(self, interval: float = 1.0):
        """
        最適化を開始
        
        Args:
            interval: 監視間隔（秒）
        """
        if self.running:
            return
        
        self.running = True
        self.thread = threading.Thread(target=self._optimization_loop, args=(interval,))
        self.thread.daemon = True
        self.thread.start()
        
        logger.info(f"Energy optimization started with target CPU usage: {self.target_cpu_usage}%")
    
    def stop(self):
        """最適化を停止"""
        self.running = False
        
        if self.thread:
            self.thread.join(timeout=2.0)
        
        logger.info("Energy optimization stopped")
    
    def register_throttle_callback(self, callback: Callable[[float], None]):
        """
        スロットリングコールバックを登録
        
        Args:
            callback: スロットリング率（0.0〜1.0）を受け取るコールバック関数
        """
        self.throttle_callbacks.append(callback)
    
    def _optimization_loop(self, interval: float):
        """
        最適化ループ
        
        Args:
            interval: 監視間隔（秒）
        """
        while self.running:
            try:
                # CPU使用率を取得
                cpu_usage = psutil.cpu_percent(interval=0.1)
                
                # スロットリング率を計算（0.0〜1.0）
                # CPU使用率が目標を超えるほど、スロットリング率が高くなる
                if cpu_usage > self.target_cpu_usage:
                    throttle_rate = min((cpu_usage - self.target_cpu_usage) / 100.0, 0.9)
                else:
                    throttle_rate = 0.0
                
                # メモリ使用率を取得
                memory_usage = psutil.virtual_memory().percent
                
                # メモリ使用率が高い場合、スロットリング率を上げる
                if memory_usage > 80.0:
                    throttle_rate = max(throttle_rate, (memory_usage - 80.0) / 100.0)
                
                # バッテリー状態を考慮（可能な場合）
                if hasattr(psutil, "sensors_battery"):
                    battery = psutil.sensors_battery()
                    if battery and not battery.power_plugged and battery.percent < 20.0:
                        # バッテリー残量が少ない場合、スロットリング率を上げる
                        throttle_rate = max(throttle_rate, (20.0 - battery.percent) / 20.0)
                
                # スロットリングコールバックを呼び出し
                for callback in self.throttle_callbacks:
                    try:
                        callback(throttle_rate)
                    except Exception as e:
                        logger.error(f"Error in throttle callback: {e}")
                
                # ログ出力（デバッグレベル）
                logger.debug(f"CPU: {cpu_usage:.1f}%, Memory: {memory_usage:.1f}%, Throttle: {throttle_rate:.2f}")
                
                # 指定された間隔でスリープ
                time.sleep(interval)
                
            except Exception as e:
                logger.error(f"Error in optimization loop: {e}")
                time.sleep(1.0)
    
    @staticmethod
    def get_system_energy_info() -> Dict[str, Any]:
        """
        システムのエネルギー情報を取得
        
        Returns:
            Dict[str, Any]: エネルギー情報
        """
        info = {
            "cpu_usage": psutil.cpu_percent(),
            "memory_usage": psutil.virtual_memory().percent,
            "disk_usage": psutil.disk_usage("/").percent,
            "battery": None,
            "temperature": None
        }
        
        # バッテリー情報（可能な場合）
        if hasattr(psutil, "sensors_battery"):
            battery = psutil.sensors_battery()
            if battery:
                info["battery"] = {
                    "percent": battery.percent,
                    "power_plugged": battery.power_plugged,
                    "secsleft": battery.secsleft
                }
        
        # 温度情報（可能な場合）
        if hasattr(psutil, "sensors_temperatures"):
            temps = psutil.sensors_temperatures()
            if temps:
                info["temperature"] = {}
                for name, entries in temps.items():
                    info["temperature"][name] = [
                        {"label": entry.label, "current": entry.current, "high": entry.high, "critical": entry.critical}
                        for entry in entries
                    ]
        
        return info