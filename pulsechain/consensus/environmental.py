"""
環境同期型コンセンサスメカニズムを実装するモジュール
"""

import time
import hashlib
import random
import json
from typing import Dict, List, Any, Optional, Tuple
from ..utils.vrf import VRF


class EnvironmentalData:
    """環境データを表すクラス"""
    
    def __init__(self, 
                 temperature: float = 0.0,
                 humidity: float = 0.0,
                 pressure: float = 0.0,
                 light: float = 0.0,
                 sound: float = 0.0,
                 vibration: float = 0.0,
                 timestamp: Optional[float] = None,
                 source_id: str = "simulator"):
        """
        環境データの初期化
        
        Args:
            temperature: 温度（℃）
            humidity: 湿度（%）
            pressure: 気圧（hPa）
            light: 光量（lux）
            sound: 音量（dB）
            vibration: 振動（m/s²）
            timestamp: タイムスタンプ（指定がなければ現在時刻）
            source_id: データソースの識別子
        """
        self.temperature = temperature
        self.humidity = humidity
        self.pressure = pressure
        self.light = light
        self.sound = sound
        self.vibration = vibration
        self.timestamp = timestamp or time.time()
        self.source_id = source_id
    
    def to_dict(self) -> Dict[str, Any]:
        """環境データを辞書形式に変換"""
        return {
            "temperature": self.temperature,
            "humidity": self.humidity,
            "pressure": self.pressure,
            "light": self.light,
            "sound": self.sound,
            "vibration": self.vibration,
            "timestamp": self.timestamp,
            "source_id": self.source_id
        }
    
    def to_json(self) -> str:
        """環境データをJSON形式に変換"""
        return json.dumps(self.to_dict(), sort_keys=True)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'EnvironmentalData':
        """辞書から環境データを生成"""
        return cls(
            temperature=data.get("temperature", 0.0),
            humidity=data.get("humidity", 0.0),
            pressure=data.get("pressure", 0.0),
            light=data.get("light", 0.0),
            sound=data.get("sound", 0.0),
            vibration=data.get("vibration", 0.0),
            timestamp=data.get("timestamp"),
            source_id=data.get("source_id", "unknown")
        )
    
    @classmethod
    def from_json(cls, json_str: str) -> 'EnvironmentalData':
        """JSON文字列から環境データを生成"""
        data = json.loads(json_str)
        return cls.from_dict(data)
    
    @classmethod
    def generate_random(cls, source_id: str = "simulator") -> 'EnvironmentalData':
        """ランダムな環境データを生成（シミュレーション用）"""
        return cls(
            temperature=random.uniform(-10, 40),
            humidity=random.uniform(0, 100),
            pressure=random.uniform(950, 1050),
            light=random.uniform(0, 100000),
            sound=random.uniform(30, 100),
            vibration=random.uniform(0, 10),
            source_id=source_id
        )


class EnvironmentalConsensus:
    """環境同期型コンセンサスメカニズム"""
    
    def __init__(self, node_id: str, private_key: str):
        """
        コンセンサスメカニズムの初期化
        
        Args:
            node_id: ノードの識別子
            private_key: VRF用の秘密鍵
        """
        self.node_id = node_id
        self.vrf = VRF(private_key)
        self.env_data_sources: List[EnvironmentalData] = []
        self.last_consensus_time = 0
        self.consensus_interval = 10  # 10秒ごとにコンセンサスを実行
    
    def add_environmental_data(self, data: EnvironmentalData) -> None:
        """環境データを追加"""
        self.env_data_sources.append(data)
        
        # 古いデータを削除（1時間以上前のデータ）
        current_time = time.time()
        self.env_data_sources = [
            d for d in self.env_data_sources 
            if current_time - d.timestamp < 3600
        ]
    
    def _hash_environmental_data(self) -> str:
        """すべての環境データをハッシュ化"""
        if not self.env_data_sources:
            # データがない場合はランダムなデータを生成
            self.add_environmental_data(EnvironmentalData.generate_random())
        
        # すべてのデータをJSON形式に変換して連結
        combined_data = "".join([d.to_json() for d in self.env_data_sources])
        
        # SHA-256ハッシュを計算
        return hashlib.sha256(combined_data.encode()).hexdigest()
    
    def generate_random_value(self) -> Tuple[str, str]:
        """
        環境データを元に検証可能なランダム値を生成
        
        Returns:
            Tuple[str, str]: (ランダム値, 証明) のタプル
        """
        env_hash = self._hash_environmental_data()
        return self.vrf.generate(env_hash)
    
    def verify_random_value(self, value: str, proof: str, env_hash: str, public_key: str) -> bool:
        """
        ランダム値を検証
        
        Args:
            value: 検証するランダム値
            proof: ランダム値の証明
            env_hash: 環境データのハッシュ
            public_key: 検証に使用する公開鍵
            
        Returns:
            bool: 検証が成功した場合はTrue、そうでない場合はFalse
        """
        return self.vrf.verify(value, proof, env_hash, public_key)
    
    def is_leader(self, random_value: str, node_count: int) -> bool:
        """
        ノードがリーダーかどうかを判定
        
        Args:
            random_value: VRFで生成されたランダム値
            node_count: ネットワーク内のノード数
            
        Returns:
            bool: このノードがリーダーの場合はTrue、そうでない場合はFalse
        """
        # ランダム値を整数に変換
        value_int = int(random_value, 16)
        
        # ノードIDをハッシュ化して整数に変換
        node_hash = hashlib.sha256(self.node_id.encode()).hexdigest()
        node_int = int(node_hash, 16)
        
        # 両方の値を組み合わせて、ノード数で割った余りを計算
        combined = (value_int + node_int) % node_count
        
        # 余りが0の場合、このノードがリーダー
        return combined == 0
    
    def run_consensus(self, node_count: int) -> Tuple[bool, str, str]:
        """
        コンセンサスを実行
        
        Args:
            node_count: ネットワーク内のノード数
            
        Returns:
            Tuple[bool, str, str]: (リーダーかどうか, ランダム値, 証明) のタプル
        """
        current_time = time.time()
        
        # コンセンサス間隔をチェック
        if current_time - self.last_consensus_time < self.consensus_interval:
            return False, "", ""
        
        self.last_consensus_time = current_time
        
        # ランダム値を生成
        random_value, proof = self.generate_random_value()
        
        # リーダーかどうかを判定
        is_leader = self.is_leader(random_value, node_count)
        
        return is_leader, random_value, proof