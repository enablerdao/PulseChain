"""
PulseChainノードのメインアプリケーション
"""

import os
import time
import logging
import argparse
import threading
import random
from pulsechain.core.node import Node
from pulsechain.network.api_server import APIServer
from pulsechain.consensus.environmental import EnvironmentalData


# ロガーの設定
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("PulseChainMain")


def simulate_environmental_data(node: Node, interval: float = 5.0):
    """
    環境データのシミュレーション
    
    Args:
        node: データを追加するノード
        interval: データ生成の間隔（秒）
    """
    logger.info("Starting environmental data simulation")
    
    while True:
        try:
            # ランダムな環境データを生成
            env_data = EnvironmentalData.generate_random()
            
            # ノードに環境データを追加
            node.add_environmental_data(env_data)
            
            logger.debug(f"Added environmental data: {env_data.to_dict()}")
            
            # 指定された間隔でスリープ
            time.sleep(interval)
            
        except Exception as e:
            logger.error(f"Error in environmental data simulation: {e}")
            time.sleep(1.0)


def main():
    """メイン関数"""
    parser = argparse.ArgumentParser(description="PulseChain Node")
    parser.add_argument("--port", type=int, default=52964, help="API server port")
    parser.add_argument("--host", type=str, default="0.0.0.0", help="API server host")
    parser.add_argument("--node-id", type=str, help="Node ID (optional)")
    parser.add_argument("--simulate-env", action="store_true", help="Simulate environmental data")
    parser.add_argument("--env-interval", type=float, default=5.0, 
                        help="Environmental data simulation interval (seconds)")
    
    args = parser.parse_args()
    
    try:
        # ノードの作成
        node = Node(node_id=args.node_id)
        
        # ノードの起動
        node.start()
        
        # 環境データシミュレーションの開始（オプション）
        if args.simulate_env:
            env_thread = threading.Thread(
                target=simulate_environmental_data,
                args=(node, args.env_interval)
            )
            env_thread.daemon = True
            env_thread.start()
        
        # APIサーバーの作成と実行
        api_server = APIServer(node)
        api_server.run(host=args.host, port=args.port)
        
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