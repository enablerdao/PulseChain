"""
人間的信頼形成システム（Human Trust Layer）の実装
"""

import time
import math
import json
import logging
import threading
from typing import Dict, List, Set, Optional, Tuple, Any

# ロガーの設定
logger = logging.getLogger("TrustSystem")


class TrustScore:
    """ノードの信頼スコアを表すクラス"""
    
    def __init__(self, node_id: str, initial_score: float = 50.0):
        """
        信頼スコアの初期化
        
        Args:
            node_id: スコアを付与するノードのID
            initial_score: 初期スコア（0.0〜100.0）
        """
        self.node_id = node_id
        self.score = initial_score
        self.history: List[Tuple[float, float, str]] = []  # (timestamp, score_change, reason)
        self.last_update = time.time()
        self.total_transactions = 0
        self.valid_transactions = 0
        self.invalid_transactions = 0
        self.uptime_start = time.time()
        self.total_uptime = 0.0
        self.total_downtime = 0.0
        self.is_online = True
        self.votes_received: Dict[str, float] = {}  # voter_id -> vote_value
    
    def update_score(self, change: float, reason: str) -> None:
        """
        スコアを更新
        
        Args:
            change: スコアの変化量（正または負）
            reason: 変更理由
        """
        timestamp = time.time()
        
        # スコアを更新（0.0〜100.0の範囲内に収める）
        self.score = max(0.0, min(100.0, self.score + change))
        
        # 履歴に追加
        self.history.append((timestamp, change, reason))
        
        # 履歴が長すぎる場合は古いものを削除
        if len(self.history) > 1000:
            self.history = self.history[-1000:]
        
        self.last_update = timestamp
    
    def record_transaction(self, is_valid: bool) -> None:
        """
        トランザクション処理の記録
        
        Args:
            is_valid: トランザクションが有効だったかどうか
        """
        self.total_transactions += 1
        
        if is_valid:
            self.valid_transactions += 1
            # 有効なトランザクションはスコアを少し上げる
            self.update_score(0.1, "Valid transaction processed")
        else:
            self.invalid_transactions += 1
            # 無効なトランザクションはスコアを下げる
            self.update_score(-1.0, "Invalid transaction attempted")
    
    def record_online_status(self, is_online: bool) -> None:
        """
        オンライン状態の記録
        
        Args:
            is_online: ノードがオンラインかどうか
        """
        now = time.time()
        
        if self.is_online and not is_online:
            # オンラインからオフラインに変わった
            self.total_uptime += now - self.uptime_start
            self.is_online = False
            # オフラインになるとスコアが少し下がる
            self.update_score(-0.5, "Node went offline")
        elif not self.is_online and is_online:
            # オフラインからオンラインに変わった
            self.total_downtime += now - self.uptime_start
            self.is_online = True
            self.uptime_start = now
            # オンラインに戻るとスコアが少し上がる
            self.update_score(0.2, "Node came online")
    
    def receive_vote(self, voter_id: str, vote_value: float) -> None:
        """
        他のノードからの投票を受け取る
        
        Args:
            voter_id: 投票者のノードID
            vote_value: 投票値（-10.0〜10.0）
        """
        # 投票値の範囲を制限
        vote_value = max(-10.0, min(10.0, vote_value))
        
        # 投票を記録
        self.votes_received[voter_id] = vote_value
        
        # 投票の平均値を計算
        avg_vote = sum(self.votes_received.values()) / len(self.votes_received)
        
        # 投票に基づいてスコアを更新
        vote_impact = avg_vote / 10.0  # -1.0〜1.0の範囲に正規化
        self.update_score(vote_impact, "Community vote")
    
    def get_reliability(self) -> float:
        """
        ノードの信頼性を計算
        
        Returns:
            float: 信頼性スコア（0.0〜1.0）
        """
        # トランザクション処理の信頼性
        tx_reliability = 0.5
        if self.total_transactions > 0:
            tx_reliability = self.valid_transactions / self.total_transactions
        
        # オンライン時間の信頼性
        total_time = self.total_uptime + self.total_downtime
        uptime_reliability = 0.5
        if total_time > 0:
            uptime_reliability = self.total_uptime / total_time
        
        # 信頼スコアの正規化（0.0〜1.0）
        score_reliability = self.score / 100.0
        
        # 総合的な信頼性（各要素に重みを付けて計算）
        reliability = (
            tx_reliability * 0.4 +
            uptime_reliability * 0.3 +
            score_reliability * 0.3
        )
        
        return reliability
    
    def to_dict(self) -> Dict[str, Any]:
        """信頼スコア情報を辞書形式に変換"""
        return {
            "node_id": self.node_id,
            "score": self.score,
            "last_update": self.last_update,
            "total_transactions": self.total_transactions,
            "valid_transactions": self.valid_transactions,
            "invalid_transactions": self.invalid_transactions,
            "total_uptime": self.total_uptime,
            "total_downtime": self.total_downtime,
            "is_online": self.is_online,
            "reliability": self.get_reliability(),
            "recent_history": self.history[-10:] if self.history else []
        }


class TrustSystem:
    """人間的信頼形成システム"""
    
    def __init__(self):
        """信頼システムの初期化"""
        self.trust_scores: Dict[str, TrustScore] = {}
        self.blacklisted_nodes: Set[str] = set()
        self.lock = threading.RLock()
        self.vote_threshold = -5.0  # この値以下のスコアを持つノードは自動的にブラックリストに追加
    
    def get_trust_score(self, node_id: str) -> TrustScore:
        """
        ノードの信頼スコアを取得（存在しない場合は新規作成）
        
        Args:
            node_id: ノードID
            
        Returns:
            TrustScore: 信頼スコアオブジェクト
        """
        with self.lock:
            if node_id not in self.trust_scores:
                self.trust_scores[node_id] = TrustScore(node_id)
            return self.trust_scores[node_id]
    
    def update_score(self, node_id: str, change: float, reason: str) -> None:
        """
        ノードのスコアを更新
        
        Args:
            node_id: ノードID
            change: スコアの変化量
            reason: 変更理由
        """
        with self.lock:
            if node_id in self.blacklisted_nodes:
                return
            
            trust_score = self.get_trust_score(node_id)
            trust_score.update_score(change, reason)
            
            # スコアが閾値を下回った場合はブラックリストに追加
            if trust_score.score <= self.vote_threshold:
                self.blacklisted_nodes.add(node_id)
                logger.warning(f"Node {node_id} has been blacklisted due to low trust score")
    
    def record_transaction(self, node_id: str, is_valid: bool) -> None:
        """
        トランザクション処理を記録
        
        Args:
            node_id: ノードID
            is_valid: トランザクションが有効だったかどうか
        """
        with self.lock:
            if node_id in self.blacklisted_nodes:
                return
            
            trust_score = self.get_trust_score(node_id)
            trust_score.record_transaction(is_valid)
    
    def record_online_status(self, node_id: str, is_online: bool) -> None:
        """
        オンライン状態を記録
        
        Args:
            node_id: ノードID
            is_online: ノードがオンラインかどうか
        """
        with self.lock:
            if node_id in self.blacklisted_nodes:
                return
            
            trust_score = self.get_trust_score(node_id)
            trust_score.record_online_status(is_online)
    
    def submit_vote(self, voter_id: str, target_id: str, vote_value: float) -> bool:
        """
        ノードに対する投票を提出
        
        Args:
            voter_id: 投票者のノードID
            target_id: 投票対象のノードID
            vote_value: 投票値（-10.0〜10.0）
            
        Returns:
            bool: 投票が成功したかどうか
        """
        with self.lock:
            # 自分自身への投票は無効
            if voter_id == target_id:
                return False
            
            # ブラックリストに登録されているノードは投票できない
            if voter_id in self.blacklisted_nodes:
                return False
            
            # 投票対象がブラックリストに登録されている場合は投票できない
            if target_id in self.blacklisted_nodes:
                return False
            
            # 投票者の信頼性に基づいて投票の重みを調整
            voter_score = self.get_trust_score(voter_id)
            voter_reliability = voter_score.get_reliability()
            
            # 信頼性の低い投票者の影響を抑える
            weighted_vote = vote_value * voter_reliability
            
            # 投票を記録
            target_score = self.get_trust_score(target_id)
            target_score.receive_vote(voter_id, weighted_vote)
            
            # 投票後のスコアが閾値を下回った場合はブラックリストに追加
            if target_score.score <= self.vote_threshold:
                self.blacklisted_nodes.add(target_id)
                logger.warning(f"Node {target_id} has been blacklisted due to community votes")
            
            return True
    
    def is_blacklisted(self, node_id: str) -> bool:
        """
        ノードがブラックリストに登録されているかどうかを確認
        
        Args:
            node_id: ノードID
            
        Returns:
            bool: ブラックリストに登録されている場合はTrue
        """
        with self.lock:
            return node_id in self.blacklisted_nodes
    
    def get_all_scores(self) -> Dict[str, Dict[str, Any]]:
        """
        すべてのノードの信頼スコア情報を取得
        
        Returns:
            Dict[str, Dict[str, Any]]: ノードIDをキーとする信頼スコア情報の辞書
        """
        with self.lock:
            return {
                node_id: score.to_dict()
                for node_id, score in self.trust_scores.items()
            }
    
    def get_trusted_nodes(self, min_reliability: float = 0.7) -> List[str]:
        """
        信頼性の高いノードのリストを取得
        
        Args:
            min_reliability: 最小信頼性（0.0〜1.0）
            
        Returns:
            List[str]: 信頼性の高いノードのIDリスト
        """
        with self.lock:
            return [
                node_id
                for node_id, score in self.trust_scores.items()
                if score.get_reliability() >= min_reliability
                and node_id not in self.blacklisted_nodes
            ]
    
    def save_to_file(self, filename: str) -> bool:
        """
        信頼システムの状態をファイルに保存
        
        Args:
            filename: 保存先のファイル名
            
        Returns:
            bool: 保存に成功した場合はTrue
        """
        try:
            with self.lock:
                data = {
                    "trust_scores": {
                        node_id: score.to_dict()
                        for node_id, score in self.trust_scores.items()
                    },
                    "blacklisted_nodes": list(self.blacklisted_nodes),
                    "vote_threshold": self.vote_threshold
                }
                
                with open(filename, 'w') as f:
                    json.dump(data, f, indent=2)
                
                return True
        except Exception as e:
            logger.error(f"Error saving trust system to file: {e}")
            return False
    
    @classmethod
    def load_from_file(cls, filename: str) -> Optional['TrustSystem']:
        """
        ファイルから信頼システムの状態を読み込む
        
        Args:
            filename: 読み込むファイル名
            
        Returns:
            Optional[TrustSystem]: 読み込んだ信頼システム、エラー時はNone
        """
        try:
            with open(filename, 'r') as f:
                data = json.load(f)
            
            trust_system = cls()
            
            # ブラックリストを復元
            trust_system.blacklisted_nodes = set(data.get("blacklisted_nodes", []))
            
            # 投票閾値を復元
            trust_system.vote_threshold = data.get("vote_threshold", -5.0)
            
            # 信頼スコアを復元
            for node_id, score_data in data.get("trust_scores", {}).items():
                trust_score = TrustScore(node_id, score_data.get("score", 50.0))
                trust_score.last_update = score_data.get("last_update", time.time())
                trust_score.total_transactions = score_data.get("total_transactions", 0)
                trust_score.valid_transactions = score_data.get("valid_transactions", 0)
                trust_score.invalid_transactions = score_data.get("invalid_transactions", 0)
                trust_score.total_uptime = score_data.get("total_uptime", 0.0)
                trust_score.total_downtime = score_data.get("total_downtime", 0.0)
                trust_score.is_online = score_data.get("is_online", True)
                
                trust_system.trust_scores[node_id] = trust_score
            
            return trust_system
            
        except Exception as e:
            logger.error(f"Error loading trust system from file: {e}")
            return None