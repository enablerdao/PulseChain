#!/usr/bin/env python3
"""
PulseChain API Server
---------------------
ネットワーク統計情報を提供するRESTful API
"""

import os
import json
import time
import random
import logging
import datetime
import threading
import sqlite3
from typing import Dict, List, Any, Optional
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# ロギング設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("api_server")

# データベースファイル
DB_FILE = "pulsechain_stats.db"

# FastAPIアプリケーション
app = FastAPI(
    title="PulseChain API",
    description="PulseChainネットワークの統計情報を提供するAPI",
    version="1.0.0"
)

# CORS設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 本番環境では特定のオリジンのみ許可する
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# データベース初期化
def init_db():
    """データベースを初期化"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # ノード統計テーブル
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS node_stats (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT NOT NULL,
        total_nodes INTEGER NOT NULL,
        active_nodes INTEGER NOT NULL,
        validator_nodes INTEGER NOT NULL
    )
    ''')
    
    # トランザクション統計テーブル
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS tx_stats (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT NOT NULL,
        total_tx INTEGER NOT NULL,
        daily_tx INTEGER NOT NULL,
        pending_tx INTEGER NOT NULL
    )
    ''')
    
    # パフォーマンス統計テーブル
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS performance_stats (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT NOT NULL,
        current_tps REAL NOT NULL,
        peak_tps REAL NOT NULL,
        avg_block_time REAL NOT NULL
    )
    ''')
    
    # ブロック統計テーブル
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS block_stats (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT NOT NULL,
        latest_block INTEGER NOT NULL,
        avg_block_time REAL NOT NULL
    )
    ''')
    
    # ネットワーク統計テーブル
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS network_stats (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT NOT NULL,
        total_staked INTEGER NOT NULL,
        active_validators INTEGER NOT NULL
    )
    ''')
    
    # 地域分布テーブル
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS region_distribution (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT NOT NULL,
        region TEXT NOT NULL,
        percentage REAL NOT NULL
    )
    ''')
    
    # TPS履歴テーブル
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS tps_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT NOT NULL,
        hour TEXT NOT NULL,
        tps REAL NOT NULL
    )
    ''')
    
    # トランザクション履歴テーブル
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS tx_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT NOT NULL,
        date TEXT NOT NULL,
        count INTEGER NOT NULL
    )
    ''')
    
    # バリデーターテーブル
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS validators (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT NOT NULL,
        name TEXT NOT NULL,
        country TEXT NOT NULL,
        nodes INTEGER NOT NULL,
        uptime REAL NOT NULL,
        staked INTEGER NOT NULL
    )
    ''')
    
    conn.commit()
    conn.close()
    
    logger.info("データベースを初期化しました")

# 初期データの生成
def generate_initial_data():
    """初期データを生成してデータベースに保存"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # 現在の日時
    now = datetime.datetime.now().isoformat()
    
    # ノード数
    total_nodes = 1250 + random.randint(0, 50)
    active_nodes = total_nodes - random.randint(0, 30)
    validator_nodes = 500 + random.randint(0, 20)
    
    cursor.execute(
        "INSERT INTO node_stats (timestamp, total_nodes, active_nodes, validator_nodes) VALUES (?, ?, ?, ?)",
        (now, total_nodes, active_nodes, validator_nodes)
    )
    
    # トランザクション数
    daily_tx = 1200000 + random.randint(0, 200000)
    total_tx = 156000000 + daily_tx
    pending_tx = random.randint(0, 1000)
    
    cursor.execute(
        "INSERT INTO tx_stats (timestamp, total_tx, daily_tx, pending_tx) VALUES (?, ?, ?, ?)",
        (now, total_tx, daily_tx, pending_tx)
    )
    
    # パフォーマンス
    current_tps = 10 + random.randint(0, 5)
    peak_tps = 120
    avg_block_time = 2.5 + (random.random() * 0.5 - 0.25)
    
    cursor.execute(
        "INSERT INTO performance_stats (timestamp, current_tps, peak_tps, avg_block_time) VALUES (?, ?, ?, ?)",
        (now, current_tps, peak_tps, avg_block_time)
    )
    
    # ブロック情報
    latest_block = 4582000 + random.randint(0, 100)
    
    cursor.execute(
        "INSERT INTO block_stats (timestamp, latest_block, avg_block_time) VALUES (?, ?, ?)",
        (now, latest_block, avg_block_time)
    )
    
    # ネットワーク情報
    total_staked = 500000000 + random.randint(0, 1000000)
    active_validators = validator_nodes
    
    cursor.execute(
        "INSERT INTO network_stats (timestamp, total_staked, active_validators) VALUES (?, ?, ?)",
        (now, total_staked, active_validators)
    )
    
    # 地域分布
    regions = [
        ("アジア", 35 + random.randint(0, 5)),
        ("北米", 30 + random.randint(0, 5)),
        ("ヨーロッパ", 25 + random.randint(0, 5)),
        ("その他", 10 + random.randint(0, 3))
    ]
    
    # 合計が100%になるように調整
    total = sum(percentage for _, percentage in regions)
    regions = [(region, round(percentage / total * 100)) for region, percentage in regions]
    
    for region, percentage in regions:
        cursor.execute(
            "INSERT INTO region_distribution (timestamp, region, percentage) VALUES (?, ?, ?)",
            (now, region, percentage)
        )
    
    # 過去24時間のTPSデータ
    current_hour = datetime.datetime.now().hour
    for i in range(24):
        hour = (current_hour - 23 + i) % 24
        hour_str = f"{hour}:00"
        tps = 5 + random.randint(0, 15)
        
        cursor.execute(
            "INSERT INTO tps_history (timestamp, hour, tps) VALUES (?, ?, ?)",
            (now, hour_str, tps)
        )
    
    # 過去7日間のトランザクション数
    for i in range(7):
        date = datetime.datetime.now() - datetime.timedelta(days=6-i)
        date_str = date.strftime("%m/%d")
        count = 800000 + random.randint(0, 400000)
        
        cursor.execute(
            "INSERT INTO tx_history (timestamp, date, count) VALUES (?, ?, ?)",
            (now, date_str, count)
        )
    
    # トップバリデーター
    validators = [
        ("PulseNode Tokyo", "日本", 25, 99.98, 25000000),
        ("Quantum Validators", "アメリカ", 22, 99.95, 22000000),
        ("Berlin Pulse", "ドイツ", 18, 99.92, 18000000),
        ("SG Validators", "シンガポール", 15, 99.90, 15000000),
        ("Maple Leaf Nodes", "カナダ", 12, 99.89, 12000000),
        ("London Bridge", "イギリス", 10, 99.87, 10000000),
        ("Paris Pulse", "フランス", 9, 99.85, 9000000),
        ("Sydney Stakers", "オーストラリア", 8, 99.82, 8000000),
        ("Seoul Secure", "韓国", 7, 99.80, 7000000),
        ("Dragon Validators", "中国", 6, 99.78, 6000000)
    ]
    
    for name, country, nodes, uptime, staked in validators:
        cursor.execute(
            "INSERT INTO validators (timestamp, name, country, nodes, uptime, staked) VALUES (?, ?, ?, ?, ?, ?)",
            (now, name, country, nodes, uptime, staked)
        )
    
    conn.commit()
    conn.close()
    
    logger.info("初期データを生成しました")

# データ更新スレッド
def update_data_thread():
    """定期的にデータを更新するスレッド"""
    while True:
        try:
            conn = sqlite3.connect(DB_FILE)
            cursor = conn.cursor()
            
            # 現在の日時
            now = datetime.datetime.now().isoformat()
            
            # 最新のノード統計を取得
            cursor.execute("SELECT total_nodes, active_nodes, validator_nodes FROM node_stats ORDER BY id DESC LIMIT 1")
            total_nodes, active_nodes, validator_nodes = cursor.fetchone()
            
            # ノード数を更新（小さな変動を加える）
            total_nodes = total_nodes + random.randint(-5, 10)
            active_nodes = min(total_nodes, active_nodes + random.randint(-3, 5))
            validator_nodes = min(active_nodes, validator_nodes + random.randint(-2, 3))
            
            cursor.execute(
                "INSERT INTO node_stats (timestamp, total_nodes, active_nodes, validator_nodes) VALUES (?, ?, ?, ?)",
                (now, total_nodes, active_nodes, validator_nodes)
            )
            
            # 最新のトランザクション統計を取得
            cursor.execute("SELECT total_tx, daily_tx, pending_tx FROM tx_stats ORDER BY id DESC LIMIT 1")
            total_tx, daily_tx, pending_tx = cursor.fetchone()
            
            # トランザクション数を更新
            new_tx = random.randint(100, 1000)
            total_tx += new_tx
            daily_tx += new_tx
            pending_tx = max(0, pending_tx + random.randint(-100, 150))
            
            cursor.execute(
                "INSERT INTO tx_stats (timestamp, total_tx, daily_tx, pending_tx) VALUES (?, ?, ?, ?)",
                (now, total_tx, daily_tx, pending_tx)
            )
            
            # パフォーマンス統計を更新
            current_tps = 10 + random.randint(0, 5)
            peak_tps = 120
            avg_block_time = 2.5 + (random.random() * 0.5 - 0.25)
            
            cursor.execute(
                "INSERT INTO performance_stats (timestamp, current_tps, peak_tps, avg_block_time) VALUES (?, ?, ?, ?)",
                (now, current_tps, peak_tps, avg_block_time)
            )
            
            # ブロック情報を更新
            cursor.execute("SELECT latest_block FROM block_stats ORDER BY id DESC LIMIT 1")
            latest_block = cursor.fetchone()[0]
            latest_block += random.randint(1, 5)
            
            cursor.execute(
                "INSERT INTO block_stats (timestamp, latest_block, avg_block_time) VALUES (?, ?, ?)",
                (now, latest_block, avg_block_time)
            )
            
            # ネットワーク情報を更新
            cursor.execute("SELECT total_staked FROM network_stats ORDER BY id DESC LIMIT 1")
            total_staked = cursor.fetchone()[0]
            total_staked += random.randint(-100000, 200000)
            
            cursor.execute(
                "INSERT INTO network_stats (timestamp, total_staked, active_validators) VALUES (?, ?, ?)",
                (now, total_staked, validator_nodes)
            )
            
            # TPS履歴を更新
            current_hour = datetime.datetime.now().hour
            hour_str = f"{current_hour}:00"
            
            cursor.execute("DELETE FROM tps_history WHERE hour = ?", (hour_str,))
            cursor.execute(
                "INSERT INTO tps_history (timestamp, hour, tps) VALUES (?, ?, ?)",
                (now, hour_str, current_tps)
            )
            
            # 今日のトランザクション履歴を更新
            today = datetime.datetime.now().strftime("%m/%d")
            
            cursor.execute("SELECT id FROM tx_history WHERE date = ?", (today,))
            if cursor.fetchone():
                cursor.execute("UPDATE tx_history SET count = ? WHERE date = ?", (daily_tx, today))
            else:
                cursor.execute(
                    "INSERT INTO tx_history (timestamp, date, count) VALUES (?, ?, ?)",
                    (now, today, daily_tx)
                )
            
            # バリデーター情報を更新（アップタイムと小さな変動）
            cursor.execute("SELECT name, country, nodes, uptime, staked FROM validators")
            validators = cursor.fetchall()
            
            for name, country, nodes, uptime, staked in validators:
                # アップタイムを少し変動させる（99.5%〜100%の範囲内）
                new_uptime = max(99.5, min(100, uptime + (random.random() * 0.1 - 0.05)))
                
                # ステーキング量を少し変動させる
                new_staked = max(1000000, staked + random.randint(-50000, 100000))
                
                cursor.execute(
                    "UPDATE validators SET timestamp = ?, uptime = ?, staked = ? WHERE name = ?",
                    (now, new_uptime, new_staked, name)
                )
            
            conn.commit()
            conn.close()
            
            logger.info("データを更新しました")
            
            # 30秒待機
            time.sleep(30)
            
        except Exception as e:
            logger.error(f"データ更新中にエラーが発生しました: {e}")
            time.sleep(10)  # エラー時は10秒待機

# APIレスポンスモデル
class NetworkStatsResponse(BaseModel):
    timestamp: str
    nodes: Dict[str, int]
    transactions: Dict[str, int]
    performance: Dict[str, Any]
    blocks: Dict[str, Any]
    network: Dict[str, Any]
    history: Dict[str, List[Dict[str, Any]]]
    topValidators: List[Dict[str, Any]]

# APIエンドポイント
@app.get("/api/stats", response_model=NetworkStatsResponse)
async def get_network_stats():
    """ネットワーク統計情報を取得"""
    try:
        conn = sqlite3.connect(DB_FILE)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # 現在の日時
        now = datetime.datetime.now().isoformat()
        
        # ノード統計
        cursor.execute("SELECT total_nodes, active_nodes, validator_nodes FROM node_stats ORDER BY id DESC LIMIT 1")
        node_stats = cursor.fetchone()
        
        # トランザクション統計
        cursor.execute("SELECT total_tx, daily_tx, pending_tx FROM tx_stats ORDER BY id DESC LIMIT 1")
        tx_stats = cursor.fetchone()
        
        # パフォーマンス統計
        cursor.execute("SELECT current_tps, peak_tps, avg_block_time FROM performance_stats ORDER BY id DESC LIMIT 1")
        performance_stats = cursor.fetchone()
        
        # ブロック情報
        cursor.execute("SELECT latest_block, avg_block_time FROM block_stats ORDER BY id DESC LIMIT 1")
        block_stats = cursor.fetchone()
        
        # ネットワーク情報
        cursor.execute("SELECT total_staked, active_validators FROM network_stats ORDER BY id DESC LIMIT 1")
        network_stats = cursor.fetchone()
        
        # 地域分布
        cursor.execute("SELECT region, percentage FROM region_distribution ORDER BY id DESC LIMIT 4")
        region_distribution = [dict(row) for row in cursor.fetchall()]
        
        # TPS履歴
        cursor.execute("SELECT hour, tps FROM tps_history ORDER BY id DESC LIMIT 24")
        tps_history = [dict(row) for row in cursor.fetchall()]
        
        # トランザクション履歴
        cursor.execute("SELECT date, count FROM tx_history ORDER BY id DESC LIMIT 7")
        tx_history = [dict(row) for row in cursor.fetchall()]
        
        # バリデーター情報
        cursor.execute("SELECT name, country, nodes, uptime, staked FROM validators ORDER BY staked DESC LIMIT 10")
        validators = [dict(row) for row in cursor.fetchall()]
        
        conn.close()
        
        # レスポンスデータの構築
        response = {
            "timestamp": now,
            "nodes": {
                "total": node_stats["total_nodes"],
                "active": node_stats["active_nodes"],
                "validators": node_stats["validator_nodes"]
            },
            "transactions": {
                "total": tx_stats["total_tx"],
                "daily": tx_stats["daily_tx"],
                "pending": tx_stats["pending_tx"]
            },
            "performance": {
                "currentTps": performance_stats["current_tps"],
                "peakTps": performance_stats["peak_tps"],
                "tpsHistory": tps_history
            },
            "blocks": {
                "latest": block_stats["latest_block"],
                "avgTime": block_stats["avg_block_time"]
            },
            "network": {
                "totalStaked": network_stats["total_staked"],
                "activeValidators": network_stats["active_validators"],
                "regionDistribution": region_distribution
            },
            "history": {
                "tps": tps_history,
                "transactions": tx_history
            },
            "topValidators": validators
        }
        
        return response
        
    except Exception as e:
        logger.error(f"統計情報の取得中にエラーが発生しました: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

@app.get("/api/health")
async def health_check():
    """ヘルスチェックエンドポイント"""
    return {"status": "ok", "timestamp": datetime.datetime.now().isoformat()}

# サーバー起動
if __name__ == "__main__":
    # データベース初期化
    init_db()
    
    # 初期データがなければ生成
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM node_stats")
    count = cursor.fetchone()[0]
    conn.close()
    
    if count == 0:
        generate_initial_data()
    
    # データ更新スレッドを開始
    update_thread = threading.Thread(target=update_data_thread, daemon=True)
    update_thread.start()
    
    # サーバー起動
    port = int(os.environ.get("PORT", 52964))
    uvicorn.run(app, host="0.0.0.0", port=port)